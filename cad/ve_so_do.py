from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle
out=Path(__file__).parent
fig,(a,b)=plt.subplots(1,2,figsize=(13,8))
fig.suptitle('ROBOT HAI BÁNH — PHÁC THẢO CƠ KHÍ THAM KHẢO',fontsize=15,fontweight='bold')
for ax in (a,b):
    ax.set_aspect('equal'); ax.set_ylim(-115,640); ax.axis('off')
    ax.plot([-190,190],[0,0],color='#525f70',lw=1)
a.set_title('NHÌN TỪ TRƯỚC',fontweight='bold');a.set_xlim(-205,205)
for x in (-100,100):
    a.add_patch(Rectangle((x-20,0),40,240,color='#222933',ec='black',lw=1.5))
    a.scatter([x],[120],c='white',s=12,zorder=5)
a.add_patch(Rectangle((-60,145),120,240,fc='#c6d6df',ec='#324553',lw=2))
a.add_patch(Rectangle((-42,165),84,72,fc='#f5db8c',ec='#a38437'))
a.text(0,198,'PIN\n(gợi ý)',ha='center',va='center',fontsize=9)
a.add_patch(Rectangle((-42,260),84,56,fc='#c4e6ca',ec='#508460'))
a.text(0,288,'PI 4\n(gợi ý)',ha='center',va='center',fontsize=9)
a.add_patch(Rectangle((-55,425),110,70,fc='#8fa5b5',ec='#324553',lw=2));a.text(0,459,'ĐẦU',ha='center')
a.plot([-38,-38],[495,575],color='#324553',lw=4);a.plot([38,38],[495,575],color='#324553',lw=4)
a.annotate('',xy=(-100,-40),xytext=(100,-40),arrowprops=dict(arrowstyle='<->',lw=1));a.text(0,-56,'200 mm tâm bánh',ha='center',va='top',fontsize=9)
a.annotate('',xy=(-120,-85),xytext=(120,-85),arrowprops=dict(arrowstyle='<->',lw=1));a.text(0,-100,'240 mm phủ bì bánh',ha='center',va='top',fontsize=9)
a.text(0,70,'160 mm lọt lòng',ha='center',fontsize=8)
b.set_title('NHÌN TỪ BÊN',fontweight='bold');b.set_xlim(-200,200)
b.add_patch(Circle((0,120),120,fc='#222933',ec='black',alpha=.85))
b.add_patch(Rectangle((-65,145),130,240,fc='#c6d6df',ec='#324553',lw=2,alpha=.8))
b.add_patch(Rectangle((-55,425),110,70,fc='#8fa5b5',ec='#324553',lw=2));b.text(0,459,'ĐẦU',ha='center')
b.plot([0,0],[495,575],color='#324553',lw=4)
b.annotate('',xy=(-160,0),xytext=(-160,240),arrowprops=dict(arrowstyle='<->'));b.text(-170,120,'Ø 240 mm',rotation=90,ha='center',va='center')
b.annotate('Tâm trục cao 120 mm',xy=(0,120),xytext=(25,65),arrowprops=dict(arrowstyle='->'),fontsize=9)
b.annotate('Vị trí pin, motor,\nvỏ và servo cần đo thật',xy=(20,275),xytext=(55,330),fontsize=8)
fig.text(.5,.02,'KÍCH THƯỚC GIẢ ĐỊNH • Không dùng trực tiếp để cắt khung chịu lực hoặc đặt mua bộ truyền động',ha='center',fontsize=10,color='#9f3333')
fig.savefig(out/'00_so_do_tham_khao.svg',bbox_inches='tight')
fig.savefig(out/'00_so_do_tham_khao.png',dpi=150,bbox_inches='tight')
