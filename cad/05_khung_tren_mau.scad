/* TAM THAN TREN MAU, KHONG CHIU LUC. Don vi mm.
 * Ghep chong 40 mm: khe y=20 tam tren thang hang khe y=130 tam duoi.
 */
$fn=40;
w=130; h=130; t=4;
module slot(x,y,len=12,d=4.4){translate([x,y,-.1])linear_extrude(height=t+.2) hull(){translate([-(len-d)/2,0])circle(d=d);translate([(len-d)/2,0])circle(d=d);}}
difference(){
 cube([w,h,t]);
 for(x=[20,110],y=[20,60,110])slot(x,y);
 for(x=[43,87],y=[45,85]) translate([x,y,-.1])cylinder(h=t+.2,d=22);
}
