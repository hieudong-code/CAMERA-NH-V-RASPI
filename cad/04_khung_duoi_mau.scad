/* TAM THAN DUOI MAU, MAU THU LAP DAT KHONG CHIU LUC. Don vi mm.
 * Khong co lo gan motor/truc; phai thiet ke lai khi co ban ve motor va goi do.
 * Tam tren + duoi chong 40 mm, khe x=20/110, y=130 tuong ung y=20 tam tren.
 */
$fn=40;
w=130; h=150; t=4;
module slot(x,y,len=12,d=4.4){translate([x,y,-.1])linear_extrude(height=t+.2) hull(){translate([-(len-d)/2,0])circle(d=d);translate([(len-d)/2,0])circle(d=d);}}
difference(){
 cube([w,h,t]);
 for(x=[20,110],y=[20,60,100,130])slot(x,y);
 for(x=[43,87],y=[48,90]) translate([x,y,-.1])cylinder(h=t+.2,d=22);
}
