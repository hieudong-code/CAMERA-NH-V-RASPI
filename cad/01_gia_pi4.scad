/*
 * Raspberry Pi 4 Model B plate, experimental duck robot retrofit.
 * Coordinates in mm. PCB corner is (0,0), PCB outline x 0..85 y 0..56.
 * Official RPi 4 mechanical drawing: https://datasheets.raspberrypi.com/rpi4/raspberry-pi-4-mechanical-drawing.pdf
 * Mounting-hole centres (3.5,3.5), (61.5,3.5), (3.5,52.5), (61.5,52.5).
 * Printed flat on z=0 without supports. The board is above four pillars.
 * Outer slotted ears give adjustable interfaces, NOT verified to match any robot.
 * Fasten board using M2.5 nylon screws, washers and nuts; head clearance and
 * nut fit depend on screw/nut supplier. Verify clearances on a dry fit.
 */
$fn = 48;
board_length = 85;
board_width = 56;
base_t = 3;
standoff_height = 6;  // clear space between PCB underside and plate top
standoff_d = 6;
board_hole_d = 2.8;
ear_width = 10;
slot_width = 3.4;
slot_total_length = 16;
// No electronics model is included; measure connector and wire clearance.
assert(base_t >= 2 && standoff_height >= 4);
assert(slot_total_length > slot_width && ear_width > slot_width + 3);
board_holes = [[3.5,3.5],[61.5,3.5],[3.5,52.5],[61.5,52.5]];
module mounting_slot(cx,cy) {
    translate([cx,cy,-0.1])
        linear_extrude(height=base_t+0.2)
            hull() {
                translate([-(slot_total_length-slot_width)/2,0]) circle(d=slot_width);
                translate([(slot_total_length-slot_width)/2,0]) circle(d=slot_width);
            }
}
module plate() {
    difference() {
        union() {
            // Flat deck plus two mounting ears outside the PCB outline.
            translate([0,-ear_width,0]) cube([board_length,board_width+2*ear_width,base_t]);
            for (p=board_holes)
                translate([p[0],p[1],base_t]) cylinder(h=standoff_height,d=standoff_d);
        }
        // Pi holes stay clear through the base; use an external nut/washer.
        for (p=board_holes)
            translate([p[0],p[1],-0.1]) cylinder(h=base_t+standoff_height+0.2,d=board_hole_d);
        // Four 16 x 3.4 mm slots; positions may be customized after measuring chassis.
        for (x=[20,65], y=[-ear_width/2,board_width+ear_width/2]) mounting_slot(x,y);
        // Ventilation / lightening holes; isolated from supports and ear slots.
        for (x=[13:12:73],y=[13:10:43])
            translate([x,y,-0.1]) cylinder(h=base_t+0.2,d=6);
    }
}
plate();
