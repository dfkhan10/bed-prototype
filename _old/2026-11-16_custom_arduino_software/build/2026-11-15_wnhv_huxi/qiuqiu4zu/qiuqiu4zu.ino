#include <Servo.h>
// 创建对象
Servo servo_2;
Servo servo_3;
Servo servo_4;
Servo servo_5;
Servo servo_6;
Servo servo_7;
Servo servo_8;
Servo servo_9;
Servo servo_10;
Servo servo_11;
Servo servo_12;
Servo servo_13;
//这是多组代码  最大可以插4组。并且需要控制板上下独立供电。请注意：上面扩展板有跳线帽一定要拔掉，否则大电流回流主板烧毁主板。扩展板独立供电要求5v 大于10a电源
//2-13为主板引脚，第一组（2插充气泵，，3插三通电磁阀，4插抽气泵。）///////（第二组：5插充气泵，6插三通电磁阀，7插抽气泵）/////（第三组：8插充气泵，9插三通电磁阀，10插抽气泵）/////（第四组：11插充气泵，12插三通电磁阀，13插抽气泵.）
// 主程序开始
void setup() {
  servo_2.attach(2);
  servo_3.attach(3);
  servo_4.attach(4);
//第一组
  servo_5.attach(5);
  servo_6.attach(6);
  servo_7.attach(7);
//第二组
  servo_8.attach(8);
  servo_9.attach(9);
  servo_10.attach(10);
//第三组
  servo_11.attach(11);
  servo_12.attach(12);
  servo_13.attach(13);
//第四组

  for (int index = 0; index < 3; index++) {   //注释：工作循环次数0-？次循环，此代表循环3次。3可以根据自己需求修改

    servo_2.write(180);
    servo_3.write(180);
    servo_4.write(0);

    servo_5.write(180);
    servo_6.write(180);
    servo_7.write(0);

    servo_8.write(180);
    servo_9.write(180);
    servo_10.write(0);

    servo_11.write(180);
    servo_12.write(180);
    servo_13.write(0);
    
    delay(8000);
//---------此组代码表示充气泵和电磁阀工作8秒（180代表开，0代表关。 delay(8000);代表运行时间为8000毫秒。需要充气时间可以按需求自定义修改。

  

    servo_2.write(0);
    servo_3.write(0);
    servo_4.write(180);

    servo_5.write(0);
    servo_6.write(0);
    servo_7.write(180);

    servo_8.write(0);
    servo_9.write(0);
    servo_10.write(180);

    servo_11.write(0);
    servo_12.write(0);
    servo_13.write(180);
    
    delay(8000);


  //--------此组代码表示抽气泵工作8秒，也就是抽气8秒（时间可以根据自己需求修改）。


    servo_2.write(0);
    servo_3.write(0);
    servo_4.write(0);

    servo_5.write(0);
    servo_6.write(0);
    servo_7.write(0);

    servo_8.write(0);
    servo_9.write(0);
    servo_10.write(0);

    servo_11.write(0);
    servo_12.write(0);
    servo_13.write(0);
    //------------------------------------全部结束。
  
  }
}
void loop() {

}
