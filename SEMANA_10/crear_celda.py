from robodk.robolink import *
from robodk.robomath import *

# ============ PARÁMETROS (solo si algo no cuadra) ============
GAP        = 2400   # mm entre base 1 y base 2 (eje X)
BELT_START = 500    # mm desde base 1: donde el robot 1 deja la caja
BELT_END   = 1900   # mm desde base 1: donde el robot 2 la recoge
CONV_DX    = 1200   # mm desde base 1: centro de la banda
CONV_DY    = 0
CONV_ROT_Z = 0      # grados; si queda atravesada, prueba 90
CONV_Z_OFF = 80     # mm para subir/bajar la banda
PLACE2_DX  = 0      # mm: dónde queda la caja en la mesa 2
PLACE2_DY  = 500
APPROACH   = 150    # mm de aproximación
BOX_H      = 150    # mm, altura del TCP sobre la caja cuando la agarra
STEPS      = 100

RDK = Robolink()
station = RDK.ActiveStation()

def check(M, nombre):
    ok = False
    try:
        ok = (M.size(0) == 4 and M.size(1) == 4)
    except Exception:
        ok = False
    if not ok:
        raise Exception('Matriz mal formada: ' + nombre)
    return M

def pose_abs(item, nombre):
    if not item.Valid():
        raise Exception('Item no válido: ' + nombre)
    try:
        return check(item.PoseAbs(), nombre)
    except Exception:
        return check(item.Parent().PoseAbs() * item.Pose(), nombre)

def hijos(item, tipo):
    return [c for c in item.Childs() if c.Type() == tipo]

def buscar(tipo, empieza=None, contiene=None, excluir=()):
    for it in RDK.ItemList(tipo):
        n = it.Name()
        if n in excluir:
            continue
        if empieza and n.startswith(empieza):
            return it
        if contiene and contiene.lower() in n.lower():
            return it
    return None

# ============ ITEMS EXISTENTES (no se borra nada) ============
print('1) Buscando items...')
base1  = RDK.Item('UR5 Base', ITEM_TYPE_FRAME)
robot1 = hijos(base1, ITEM_TYPE_ROBOT)[0]
tool1  = hijos(robot1, ITEM_TYPE_TOOL)[0]
tg = {c.Name(): c for c in hijos(base1, ITEM_TYPE_TARGET)}
home1, aprox1, pick1, aprox2, place1 = [tg[n] for n in ('home', 'aprox1', 'pick', 'aprox2', 'place')]

table1 = buscar(ITEM_TYPE_OBJECT, empieza='Table', excluir=('Table 2',))
box    = buscar(ITEM_TYPE_OBJECT, empieza='Box')
conv   = buscar(ITEM_TYPE_FRAME, contiene='conveyor')
if table1 is None or box is None or conv is None:
    raise Exception('No encuentro la mesa (Table...), la caja (Box...) o la banda (Conveyor...).')

# ============ RELACIÓN HERRAMIENTA-CAJA ============
print('2) Calculando agarre de la caja...')
if box.Parent().Type() == ITEM_TYPE_TOOL:
    tcp_now = robot1.PoseAbs() * robot1.SolveFK(robot1.Joints()) * tool1.PoseTool()
    T = check(invH(tcp_now) * box.PoseAbs(), 'T (caja en herramienta)')
    box.setParentStatic(station)
else:
    T = check(transl(0, 0, BOX_H) * rotx(pi), 'T (por defecto)')

# ============ SEGUNDO ROBOT Y MESA (copias renombradas) ============
print('3) Segundo robot y mesa...')
base2 = RDK.Item('UR5 Base 2', ITEM_TYPE_FRAME)
if not base2.Valid():
    base1.Copy()
    base2 = RDK.Paste()
    base2.setName('UR5 Base 2')
    nombres = {'home': 'home 2', 'aprox1': 'aprox1 2', 'pick': 'pick 2',
               'aprox2': 'aprox2 2', 'place': 'place 2'}
    for ch in base2.Childs():
        if ch.Name() in nombres:
            ch.setName(nombres[ch.Name()])
    table1.Copy()
    RDK.Paste().setName('Table 2')

table2 = RDK.Item('Table 2', ITEM_TYPE_OBJECT)
robot2 = hijos(base2, ITEM_TYPE_ROBOT)[0]
tool2  = hijos(robot2, ITEM_TYPE_TOOL)[0]
t2 = {c.Name(): c for c in hijos(base2, ITEM_TYPE_TARGET)}
home2, aprox12, pick2, aprox22, place2 = [t2[n] for n in ('home 2', 'aprox1 2', 'pick 2', 'aprox2 2', 'place 2')]

B1 = pose_abs(base1, 'base 1')
p1 = B1.Pos()
surf_z = p1[2]

base2.setPoseAbs(transl(GAP, 0, 0) * B1 * rotz(pi))
table2.setPoseAbs(transl(GAP, 0, 0) * pose_abs(table1, 'mesa 1'))
conv.setPoseAbs(transl(p1[0] + CONV_DX, p1[1] + CONV_DY, surf_z + CONV_Z_OFF) * rotz(CONV_ROT_Z * pi / 180))

# ============ CAJA EN SU PUNTO DE AGARRE ============
print('4) Colocando la caja en pick...')
B0 = check(pose_abs(pick1, 'pick') * T, 'B0 (caja en pick)')
box.setPoseAbs(B0)
dz = B0.Pos()[2] - surf_z
R0 = check(invH(transl(*B0.Pos())) * B0, 'R0')
zb = surf_z + dz + CONV_Z_OFF

B_start = transl(p1[0] + BELT_START, p1[1], zb) * R0
B_end   = transl(p1[0] + BELT_END,   p1[1], zb) * R0
B_dest  = transl(p1[0] + GAP + PLACE2_DX, p1[1] + PLACE2_DY, surf_z + dz) * R0

# ============ TARGETS ============
print('5) Moviendo targets...')
place1_tcp = B_start * invH(T)
place1.setPoseAbs(place1_tcp)
aprox2.setPoseAbs(transl(0, 0, APPROACH) * place1_tcp)

T2 = invH(rotz(pi)) * T
pick2_tcp  = B_end * invH(T) * rotz(pi)
place2_tcp = B_dest * invH(T2)
for t, pose in ((pick2, pick2_tcp), (place2, place2_tcp),
                (aprox12, transl(0, 0, APPROACH) * pick2_tcp),
                (aprox22, transl(0, 0, APPROACH) * place2_tcp)):
    t.setAsCartesianTarget()
    t.setPoseAbs(pose)
home2.setAsJointTarget()
home2.setJoints(home1.Joints())

# ============ PROGRAMA DEL ROBOT 2 (si no existe) ============
if not RDK.Item('Prog2', ITEM_TYPE_PROGRAM).Valid():
    prog2 = RDK.AddProgram('Prog2', robot2)
    prog2.setPoseFrame(base2)
    prog2.setPoseTool(tool2)
    prog2.MoveJ(home2); prog2.MoveJ(aprox12); prog2.MoveL(pick2)
    prog2.MoveL(aprox12); prog2.MoveJ(aprox22); prog2.MoveL(place2)
    prog2.MoveL(aprox22); prog2.MoveJ(home2)

# ============ SIMULACIÓN COMPLETA ============
print('6) Simulando...')
robot1.setPoseFrame(base1); robot1.setPoseTool(tool1)
robot2.setPoseFrame(base2); robot2.setPoseTool(tool2)

robot1.MoveJ(home1); robot1.MoveJ(aprox1); robot1.MoveL(pick1)
box.setParentStatic(tool1)
robot1.MoveL(aprox1); robot1.MoveJ(aprox2); robot1.MoveL(place1)
box.setParentStatic(station)
robot1.MoveL(aprox2); robot1.MoveJ(home1)

for i in range(STEPS + 1):
    x = p1[0] + BELT_START + (BELT_END - BELT_START) * i / STEPS
    box.setPoseAbs(transl(x, p1[1], zb) * R0)
    RDK.Render(True)
    pause(0.02)

robot2.MoveJ(home2); robot2.MoveJ(aprox12); robot2.MoveL(pick2)
box.setParentStatic(tool2)
robot2.MoveL(aprox12); robot2.MoveJ(aprox22); robot2.MoveL(place2)
box.setParentStatic(station)
robot2.MoveL(aprox22); robot2.MoveJ(home2)

print('Listo.')