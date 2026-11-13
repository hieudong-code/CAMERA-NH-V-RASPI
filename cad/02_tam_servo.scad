/* TAM GAN SERVO: ban thu co tham so, don vi mm.
 * Can do than servo va vi tri tai bat thuc te truoc khi in.
 * Khe giua gianh cho than servo; 2 khe doc danh cho tai bat servo.
 * Bon khe ngoai bat tam len thanh/khung. Khong duoc dung de do ca bo dau nang.
 */
$fn=48;
length=80; width=55; plate_t=4;
servo_l=23.5; servo_w=12.5; servo_hole_x=15.4;
slot_d=3.2; servo_slot_length=7;
frame_slot_width=3.4; frame_slot_length=12;
assert(servo_l/2 + slot_d/2 < servo_hole_x);
module slot(cx,cy,long,d,dir="x") {
 translate([cx,cy,-.1]) linear_extrude(height=plate_t+.2)
  if(dir=="x") hull(){translate([-(long-d)/2,0])circle(d=d);translate([(long-d)/2,0])circle(d=d);}
  else hull(){translate([0,-(long-d)/2])circle(d=d);translate([0,(long-d)/2])circle(d=d);}
}
difference(){
 translate([-length/2,-width/2,0])cube([length,width,plate_t]);
 translate([-servo_l/2,-servo_w/2,-.1])cube([servo_l,servo_w,plate_t+.2]);
 for (x=[-servo_hole_x,servo_hole_x]) slot(x,0,servo_slot_length,slot_d,"y");
 for (x=[-27,27],y=[-20,20])slot(x,y,frame_slot_length,frame_slot_width,"x");
}
