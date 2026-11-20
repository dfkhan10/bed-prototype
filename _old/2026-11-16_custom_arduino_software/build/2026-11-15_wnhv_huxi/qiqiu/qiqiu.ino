#include <Servo.h>
// 创建对象
Servo servo_8;
Servo servo_9;
Servo servo_10;
//8-9-10为主板引脚，8插充气泵，9插三通电磁阀。10插抽气泵。引脚可以根据自己自定义主板2-13都可以插。

// 主程序开始
void setup() {
  servo_8.attach(8);
  servo_9.attach(9);
  servo_10.attach(10);

  
  for (int index = 0; index < 3; index++) {   //注释：工作循环次数0-？次循环，此代表循环3次。3可以根据自己需求修改

    servo_8.write(180);
    servo_9.write(180);
    servo_10.write(0);
    delay(8000);
//-----------------------------------------此组代码表示充气泵和电磁阀工作8秒（180代表开，0代表关。 delay(8000);代表运行时间为8000毫秒。需要充气时间可以按需求自定义修改。



    servo_8.write(0);
    servo_9.write(0);
    servo_10.write(180);
    delay(8000);


  //---------------------------------------此组代码表示抽气泵电池阀工作8秒，也就是抽气8秒（时间可以根据自己需求修改）。


    servo_8.write(0);
    servo_9.write(0);
    servo_10.write(0);
    //------------------------------------全部结束。
  
  }
}
void loop() {

}
