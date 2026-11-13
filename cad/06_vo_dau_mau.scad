/* VO DAU MAU, CHI XEM TY LE. KHONG CO NGAM/HORN SERVO, CAN THIET KE THEM.
 * Kich thuoc ngoai 110x95x70; thanh day 2.4 mm.
 * Dat mat phang kin tren ban in, mieng rong huong len tren. Nghi nguoc khi su dung.
 * Hai lo 6.5mm la vi tri du kien cua ang ten, khong danh cho chi tiet chiu luc.
 */
$fn=48;
w=110; d=95; h=70; wall=2.4;
difference(){
 cube([w,d,h]);
 translate([wall,wall,wall]) cube([w-2*wall,d-2*wall,h-wall+.1]);
 for (x=[30,80]) translate([x,d/2,-.1])cylinder(h=wall+.2,d=6.5);
}
