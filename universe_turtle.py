"""Solar system in Python turtle. Run: python universe_turtle.py
Export MP4: pip install pillow; python universe_turtle.py --render
Export requires ffmpeg on PATH. Live view uses standard-library turtle/Tk.
The same drawing instructions use a Pillow pen for headless video export.
Sizes, distances and orbital speeds are stylized, not to scale.
"""
import math, random, sys, time
from pathlib import Path

W, H = 900, 1200  # Instagram portrait 3:4
FPS, SECONDS = 30, 24
PLANETS = [
    ('MERCURY', 67, 5, '#b5b2b0', 9),
    ('VENUS', 99, 9, '#f7cc82', 6),
    ('EARTH', 135, 11, '#37aaff', 4),
    ('MARS', 173, 8, '#ff7656', 3),
    ('JUPITER', 220, 25, '#e8b589', 2),
    ('SATURN', 275, 21, '#f3d39b', 1.5),
    ('URANUS', 330, 15, '#74e2e8', 1),
    ('NEPTUNE', 387, 15, '#527aff', .75),
]
rng = random.Random(42)
STARS = [(rng.uniform(-445,445), rng.uniform(-590,590),
          rng.choice([1,1,2,2,3]), rng.random()*6.28) for _ in range(420)]

class RasterPen:
    """Small turtle-style pen used only when exporting without a desktop."""
    def __init__(self, image):
        from PIL import ImageDraw
        self.d = ImageDraw.Draw(image); self.xy=(0,0); self.color='white'; self.width=1; self.down=False
    def pencolor(self,c): self.color=c
    def pensize(self,w): self.width=w
    def penup(self): self.down=False
    def pendown(self): self.down=True
    def goto(self,x,y):
        p=(x+W/2,H/2-y)
        if self.down: self.d.line([self.xy,p], fill=self.color, width=max(1,int(self.width)))
        self.xy=p
    def dot(self,size,color):
        x,y=self.xy; r=size/2
        self.d.ellipse((x-r,y-r,x+r,y+r),fill=color)
    def write(self,text,align='center',font=('Arial',16,'normal')):
        from PIL import ImageFont
        name='DejaVuSans-Bold.ttf' if font[2]=='bold' else 'DejaVuSans.ttf'
        f=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/'+name,font[1])
        x,y=self.xy
        self.d.text((x,y),text,font=f,fill=self.color,anchor={'center':'ms','left':'ls','right':'rs'}[align])

def line(p,pts,color,width=1):
    p.penup(); p.pencolor(color); p.pensize(width); p.goto(*pts[0]); p.pendown()
    for pt in pts[1:]: p.goto(*pt)
    p.penup()

def text(p,x,y,s,size,color='#e9efff',bold=False):
    p.penup(); p.goto(x,y); p.pencolor(color)
    p.write(s,align='center',font=('Arial',size,'bold' if bold else 'normal'))

def dot(p,x,y,r,c):
    p.penup(); p.goto(x,y); p.dot(r*2,c)

def ellipse(p,x,y,rx,ry,color,width=1,start=0,end=math.tau):
    line(p,[(x+rx*math.cos(start+(end-start)*i/100),y+ry*math.sin(start+(end-start)*i/100)) for i in range(101)],color,width)

def draw(p,t):
    # Nested strokes give an atmospheric deep-space backdrop.
    for x,y,r,phase in STARS:
        b=int(105+95*(.5+.5*math.sin(t*.8+phase)))
        dot(p,x,y,r/2,'#%02x%02x%02x'%(b,b,min(255,b+35)))
    text(p,0,504,'OUR COSMIC NEIGHBORHOOD',30,bold=True)
    text(p,0,465,'A JOURNEY THROUGH THE SOLAR SYSTEM',16,'#8ca8d9')
    cy=0; flatten=.79
    for _,a,_,_,_ in PLANETS: ellipse(p,0,cy,a,a*flatten,'#23334f')
    # Asteroid belt, between Mars and Jupiter.
    belt=random.Random(7)
    for _ in range(170):
        angle=belt.random()*math.tau+t*.018; a=belt.uniform(192,202)
        dot(p,a*math.cos(angle),cy+a*flatten*math.sin(angle),.8,'#777e96')
    # Sun corona and photosphere.
    for r,c in [(62,'#10152c'),(55,'#211c31'),(49,'#422438'),(44,'#783c35'),(39,'#c36335'),(35,'#ff9b32'),(30,'#ffc447'),(24,'#ffdc6c'),(16,'#ffe7a0')]:
        dot(p,0,cy,r,c)
    text(p,0,-58,'SUN',14,'#ffd078',True)
    for i,(name,a,r,color,speed) in enumerate(PLANETS):
        angle=i*.81 + t*.18*speed
        x=a*math.cos(angle); y=cy+a*flatten*math.sin(angle)
        # A short luminous trail shows direction of revolution.
        ellipse(p,0,cy,a,a*flatten,color,2,angle-.14,angle)
        if name=='SATURN': ellipse(p,x,y,r*1.8,r*.48,'#9d896e',5)
        dot(p,x+2,y-2,r+2,'#101827'); dot(p,x,y,r,color)
        dot(p,x-r*.27,y+r*.25,r*.57,{'EARTH':'#53c6ff','JUPITER':'#f0caa5'}.get(name,color))
        if name=='EARTH':
            # Rotating land markers represent axial spin schematically.
            for j in range(3):
                spin=t*2+j*2.1
                dot(p,x+math.sin(spin)*r*.62,y+math.cos(j*2)*r*.4,2.8,'#76d6a1')
        if name=='JUPITER':
            for dy in [-9,0,9]: line(p,[(x-r*.7,y+dy),(x+r*.7,y+dy)],'#bc875f',3)
        if name=='SATURN': ellipse(p,x,y,r*1.8,r*.48,'#edcf98',4,math.pi,math.tau)
        if name=='NEPTUNE': dot(p,x-4,y+4,3,'#90adff')
        text(p,x,y-r-21,name,13,color,True)
    text(p,0,-401,'8 PLANETS  •  ONE STAR  •  ENDLESS WONDER',18,'#cfddfb',True)
    line(p,[(-340,-438),(340,-438)],'#304867')
    text(p,0,-479,'GRAVITY KEEPS THE PLANETS IN ORBIT',20,'#ffd181',True)
    text(p,0,-516,'Inner planets travel faster • Outer planets take longer',16,'#acbddb')
    text(p,0,-555,'Artistic model • Sizes, distances and speeds are not to scale',13,'#8294b6')

def render():
    import subprocess
    from PIL import Image
    target=Path(__file__).with_name('universe_turtle.mp4')
    cmd=['ffmpeg','-y','-f','rawvideo','-vcodec','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-an','-c:v','libx264','-preset','fast','-crf','19','-pix_fmt','yuv420p','-movflags','+faststart',str(target)]
    proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.DEVNULL)
    try:
        for frame in range(FPS*SECONDS):
            im=Image.new('RGB',(W,H),'#060b1b'); draw(RasterPen(im),frame/FPS)
            if frame==0: im.save(Path(__file__).with_name('universe_preview.png'))
            proc.stdin.write(im.tobytes())
    finally:
        proc.stdin.close()
    if proc.wait(): raise RuntimeError('ffmpeg export failed')
    print(target)

def live():
    import turtle
    screen=turtle.Screen(); screen.setup(W,H); screen.bgcolor('#060b1b')
    screen.title('Our Cosmic Neighborhood | Python Turtle'); screen.tracer(0)
    p=turtle.Turtle(visible=False); p.speed(0); p.penup()
    start=time.perf_counter()
    def tick():
        p.clear(); draw(p,time.perf_counter()-start); screen.update(); screen.ontimer(tick,33)
    tick(); screen.mainloop()

if __name__=='__main__':
    render() if '--render' in sys.argv else live()
