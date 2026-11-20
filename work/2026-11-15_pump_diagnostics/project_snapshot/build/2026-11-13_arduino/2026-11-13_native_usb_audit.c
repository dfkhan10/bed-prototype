// Independent macOS/POSIX transport check. Bare board only: opening/resetting
// restarts existing firmware. Sends STK500 sync and identity reads only.
// No flash, EEPROM, fuse, erase, programming-mode or actuator commands.
#include <errno.h>
#include <fcntl.h>
#include <poll.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/file.h>
#include <sys/ioctl.h>
#include <termios.h>
#include <time.h>
#include <unistd.h>

static double began;
static double now(void) {
  struct timespec t;
  clock_gettime(CLOCK_MONOTONIC, &t);
  return t.tv_sec + t.tv_nsec / 1e9;
}
static void dump(const char *direction, const unsigned char *p, size_t n) {
  printf("%9.3f ms %s", 1000 * (now() - began), direction);
  for (size_t i = 0; i < n; ++i) printf(" %02x", p[i]);
  puts("");
  fflush(stdout);
}
static int exchange(int fd, const unsigned char *tx, size_t txlen,
                    unsigned char *rx, size_t expected, int timeout_ms) {
  dump("TX", tx, txlen);
  size_t sent = 0;
  while (sent < txlen) {
    ssize_t n = write(fd, tx + sent, txlen - sent);
    if (n < 0 && errno == EINTR) continue;
    if (n <= 0) { perror("write"); return -1; }
    sent += (size_t)n;
  }
  double deadline = now() + timeout_ms / 1000.0;
  size_t got = 0;
  while (got < expected && now() < deadline) {
    struct pollfd p = {.fd = fd, .events = POLLIN};
    int remaining = (int)((deadline - now()) * 1000);
    if (remaining < 1) remaining = 1;
    int ready = poll(&p, 1, remaining);
    if (ready < 0 && errno == EINTR) continue;
    if (ready < 0) { perror("poll"); return -1; }
    if (!ready) break;
    if (p.revents & (POLLERR | POLLHUP | POLLNVAL)) {
      fprintf(stderr, "serial poll error: %x\n", p.revents); return -1;
    }
    if (!(p.revents & POLLIN)) continue;
    ssize_t n = read(fd, rx + got, expected - got);
    if (n < 0 && (errno == EINTR || errno == EAGAIN)) continue;
    if (n <= 0) { perror("read"); return -1; }
    dump("RX", rx + got, (size_t)n);
    got += (size_t)n;
  }
  if (got != expected) printf("TIMEOUT received=%zu expected=%zu\n", got, expected);
  return (int)got;
}

int main(int argc, char **argv) {
  if (argc != 3 || (strcmp(argv[2], "57600") && strcmp(argv[2], "115200") && strcmp(argv[2], "19200"))) {
    fprintf(stderr, "Usage: %s /dev/cu.PORT 57600|115200|19200\n", argv[0]); return 2;
  }
  speed_t speed = !strcmp(argv[2], "57600") ? B57600 :
                  !strcmp(argv[2], "19200") ? B19200 : B115200;
  began = now();
  int fd = open(argv[1], O_RDWR | O_NOCTTY | O_NONBLOCK);
  if (fd < 0) { perror("open"); return 2; }
  int result = 2;
  if (flock(fd, LOCK_EX | LOCK_NB) < 0) { perror("flock"); goto done; }
  struct termios cfg;
  if (tcgetattr(fd, &cfg) < 0) { perror("tcgetattr"); goto done; }
  cfmakeraw(&cfg);
  cfg.c_cflag &= ~(CSIZE | PARENB | CSTOPB | CRTSCTS);
  cfg.c_cflag |= CS8 | CLOCAL | CREAD;
  cfg.c_iflag &= ~(IXON | IXOFF | IXANY);
  cfg.c_cc[VMIN] = 0; cfg.c_cc[VTIME] = 0;
  if (cfsetispeed(&cfg, speed) < 0 || cfsetospeed(&cfg, speed) < 0 ||
      tcsetattr(fd, TCSANOW, &cfg) < 0) { perror("termios setup"); goto done; }
  if (tcgetattr(fd, &cfg) < 0) { perror("termios readback"); goto done; }
  printf("native POSIX port=%s baud=%s actual_ispeed=%lu actual_ospeed=%lu cflag=%lx iflag=%lx memory_writes=false\n",
         argv[1], argv[2], (unsigned long)cfgetispeed(&cfg),
         (unsigned long)cfgetospeed(&cfg), (unsigned long)cfg.c_cflag,
         (unsigned long)cfg.c_iflag);
  int bits = 0;
  if (ioctl(fd, TIOCMSET, &bits) < 0) { perror("reset release"); goto done; }
  usleep(250000);
  bits = TIOCM_DTR | TIOCM_RTS;
  if (ioctl(fd, TIOCMSET, &bits) < 0) { perror("reset assert"); goto done; }
  // Match the existing held-reset probe so transport is the changed variable.
  usleep(50000);
  if (tcflush(fd, TCIFLUSH) < 0) { perror("flush startup input"); goto done; }
  const unsigned char sync[] = {0x30, 0x20};
  const unsigned char sign[] = {0x75, 0x20};
  unsigned char rx[16];
  for (int attempt = 0; attempt < 12; ++attempt) {
    int n = exchange(fd, sync, sizeof(sync), rx, 2, 350);
    if (n < 0) goto done;
    if (n == 2 && rx[0] == 0x14 && rx[1] == 0x10) {
      n = exchange(fd, sign, sizeof(sign), rx, 5, 1000);
      if (n == 5 && rx[0] == 0x14 && rx[4] == 0x10 &&
          !((rx[1] == 0 && rx[2] == 0 && rx[3] == 0) ||
            (rx[1] == 255 && rx[2] == 255 && rx[3] == 255))) {
        printf("SIGNATURE %02x%02x%02x\n", rx[1], rx[2], rx[3]); result = 0;
      } else puts("No valid signature after synchronization");
      goto done;
    }
    usleep(30000);
  }
done:
  close(fd);
  puts("PORT_CLOSED");
  return result;
}
