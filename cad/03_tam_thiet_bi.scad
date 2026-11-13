/* TAM THIET BI 120x80: khong phai tam chiu luc banh/motor.
 * Dung bat hop dien nhe len khung kim loai rieng; khe M4 co the dieu chinh.
 * Do lai vi tri thanh ngang/linh kien truoc khi in.
 */
$fn=48;
length=120; width=80; thickness=4;
module slot(x,y,len=16,d=4.4){
 translate([x,y,-.1])linear_extrude(height=thickness+.2)
 hull(){translate([-(len-d)/2,0])circle(d=d);translate([(len-d)/2,0])circle(d=d);}
}
difference(){
 cube([length,width,thickness]);
 for (x=[20,100],y=[7,73])slot(x,y);
 for (x=[20:20:100],y=[20:20:60])translate([x,y,-.1])cylinder(h=thickness+.2,d=8);
}
