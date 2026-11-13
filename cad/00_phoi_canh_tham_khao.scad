/* PHOI CANH THAM KHAO: KHONG PHAI MO HINH DE IN.
 * 240 mm duong kinh banh, khoang cach tam banh 200 mm, banh rong 40 mm.
 * Than khong bao gom motor, pin, gioang truc, duong dien hay cham soc co khi.
 */
$fn=64;
wheel_r=120; wheel_w=40; axle_spacing=200; body_w=120; body_d=130;
// Tam banh x=0, y=+-100, z=120. Truc banh theo Y, dau quay quanh Z.
color([.10,.10,.11])for(y=[-axle_spacing/2,axle_spacing/2])
 translate([0,y,wheel_r]) rotate([90,0,0]) cylinder(h=wheel_w,r=wheel_r,center=true);
color([.30,.33,.36,.8]) translate([-body_d/2,-body_w/2,145])cube([body_d,body_w,240]);
color([.22,.45,.7])translate([-35,-50,195])cube([70,100,110]); // placeholder
color([.15,.15,.16])translate([0,0,405])cylinder(h=20,d=36);
color([.2,.22,.25])translate([-55,-55,425])cube([110,110,70]); // dau tham khao
color([.1,.1,.1])for(y=[-38,38])translate([-30,y,490])cylinder(h=85,d=7);
