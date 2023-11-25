import sys
import ast
import math
from tkinter import *
from tkinter import messagebox

pi = math.pi

# Calculate azimuth function, return in radian
def azimuth(p, q):
    dx = q[0] - p[0]
    dy = q[1] - p[1]
    ang = math.atan2(dx, dy)
    if ang < 0:
        ang += 2 * math.pi
    return ang

# Calculate Forward Azimuth by giving Azimuth in (azii) & Angle (ang); in radian
def calfwdAzi(azii, ang):
    fazi = azii - 180.0 + ang
    fazi += 360.0
    return fazi % 360.0

# Calculate dE & dN function
def caldEN(a, d):
    dE = d * math.sin(a)
    dN = d * math.cos(a)
    return (dE, dN)

# Calculate e1,n1 + e2,n2
def plusPt(p, q):
    e = p[0] + q[0]
    n = p[1] + q[1]
    return (e, n)

# To converse DD.MMSSS to DD.DDDDD
def deg(d):
    is_negative = d < 0
    d = abs(d)
    dd = int(d)
    mm = int((d - dd) * 100.0000001)
    ss = (d - dd - (mm / 100.0)) * 10000.0
    r = dd + (mm / 60.0) + (ss / 3600.0)
    if is_negative: r = - r
    return r

# To converse DD.DDDDD to DD.MMSSS
def dms(dd):
    is_negative = dd < 0
    dd = abs(dd)
    mnt,sec = divmod(dd*3600,60)
    deg,mnt = divmod(mnt,60)
    r = deg + mnt/100.0 + sec/10000.0
    if is_negative: r = - r
    return r

# To convert DD.MMSSS to DD-MM-SSS
def d_m_s(d, dp=1):
    is_negative = d < 0
    d = abs(d)
    dd = int(d)
    mm = int((d - dd) * 100.0000001)
    ss = (d - dd - (mm / 100.0)) * 10000.0 + 0.000000001
    if mm<10:
        mm = '0' + str(mm)
    else:
        mm = str(mm)
    if ss<10:
        ss = '0'+ str(round(ss, dp))
    else:
        ss = str(round(ss, dp))
    if dp==0:
        ss = ss[0:-2]
    if is_negative: dd = - dd
    return '{:d}-{}-{}'.format(dd, mm, ss)

# To convert Area in square meters to Rai-Ngan-Wa, "prec" is the precision of square Wa
def r_n_w(sqm, prec=1):
    is_negative = sqm < 0
    sqm = abs(sqm)
    wa = sqm / 4.0
    rr = wa / 400.0
    r = int(rr)
    ng = int((rr - r) * 4)
    wa = wa - (r * 400) - (ng * 100)
    ng = str(ng)
    wa = str(round(wa, prec))
    if prec==0:
        wa = wa[0:-2]
    if is_negative: r = - r
    return '{:d}-{}-{}'.format(r, ng, wa)

# Status message
def statusbox(label_id, msg, nrow=4):
    label_id.config(text=msg, width=40)
    label_id.grid(row=nrow, column=2)

# Function echo message
def show_message(msg, batch=False):
    #global batch
    print(msg)
    if not batch:
        messagebox.showinfo('Information', msg)

# Function warning message
def warn_message(msg, batch=False):
    #global batch
    if batch:
        print(msg)
        sys.exit(1)
    else:
        print(msg)
        messagebox.showwarning('Warning', msg)


# Get Project Parameters from .par file
def getProjParams(fdir, inpfile):
    fctr = open(fdir + inpfile, "r")
    try:
        contents = fctr.read()
        fctr.close()
    except:
        contents = {}
    try:
        proj_dict = ast.literal_eval(contents)
    except:
        proj_dict = {}
    return proj_dict
# ====================================
def trav2pts(travpoints):
    pts = []
    for trv in travpoints:
        pt = list(trv.P)
        pt.append(0.0)                                  # Add Z=0.0 to Traverse point
        pts.append(tuple(pt))
    return pts



