import numpy as np
import matplotlib.pyplot as plt


class Node():
    def __init__(self, x, y):
        self.x = x 
        self.y = y
    
class Support():
    def __init__(self, node, supportType):
        self.node =node
        self.supportType = supportType

class PointLoad():
    def __init__(self, node, magnitude):
        self.node = node
        self.magnitude = magnitude

class Span():
    global MPointLoads
    def __init__(self, leftSupport, rightSupport, listPL=[], listUDL=[]):
        self.leftSupport = leftSupport
        self.rightSupport = rightSupport
        self.listPL = listPL
        self.listUDL = listUDL

    def length(self):
        x1 = self.leftSupport.node.x
        x2 = self.rightSupport.node.x
        L = x2 - x1
        self.L = L
        return L
    
     
    def moment(self):
        x1 = self.leftSupport.node.x
        x2 = self.rightSupport.node.x
        
        MPointLoads = [0]*len(self.listPL)
        for i in range(len(self.listPL)):
            load = self.listPL[i]
            P = load.magnitude
            xp = load.node.x
            a = xp - x1
            b = x2 - xp
            L = x2 - x1
            M = P*a*b/L
            MPointLoads[i] = M
        return MPointLoads
               
class UDL():
    def __init__(self, startSupport,endSupport, intensity):
        self.startSupport = startSupport
        self.endSupport = endSupport
        self.intensity = intensity
        
class TMSpan():
    def __init__(self, leftSpan, rightSpan):
        self.leftSpan = leftSpan
        self.rightSpan  = rightSpan

    def calculate_Ax(self):

        L_matrix = []
        L1 =  self.leftSpan.length()
        L2 =  self.rightSpan.length()
        if len(self.leftSpan.listPL) > 0:
            x1 = self.leftSpan.leftSupport.node.x
            x2 = self.leftSpan.rightSupport.node.x
            P = self.leftSpan.listPL[0].magnitude
            xp = self.leftSpan.listPL[0].node.x
            a = xp - x1
            b = x2 - xp
            L = x2 - x1
            M = P*a*b/L
            A1x1 = (1/2) * M * (xp - x1) * (2/3) * (xp - x1) + (1/2) * M * (x2 - xp) * ((xp - x1) + (1/3)*(x2 - xp))

        elif len(self.leftSpan.listUDL) > 0 :
            x1 = self.leftSpan.listUDL[0].startSupport.node.x
            x2 = self.leftSpan.listUDL[0].endSupport.node.x
            w = self.leftSpan.listUDL[0].intensity
            l = x2 - x1
            M = (w*l**2)/8
            A1x1 = (2/3) * l * M * l/2


        if len(self.rightSpan.listPL) > 0 :
            x1 = self.rightSpan.leftSupport.node.x
            x2 = self.rightSpan.rightSupport.node.x
            P = self.rightSpan.listPL[0].magnitude
            xp = self.rightSpan.listPL[0].node.x
            a = xp - x1
            b = x2 - xp
            L = x2 - x1
            M = P*a*b/L
            A2x2 = (1/2) * M * (x2 - xp) * (2/3) * (x2 - xp)  + (1/2) * M * (xp - x1) * ((x2 - xp) + (1/3)*(xp - x1))

        elif len(self.rightSpan.listUDL) > 0 :
            x1 = self.rightSpan.listUDL[0].startSupport.node.x
            x2 = self.rightSpan.listUDL[0].endSupport.node.x
            w =  self.rightSpan.listUDL[0].intensity
            l = x2 - x1
            M = (w*l**2)/8
            A2x2 = (2/3) * l * M * l/2

        return L1, L2, A1x1, A2x2


class Solver():
    def __init__(self, listofNodes, listOfSupports, listofpl, listofudl, listofTMSpan, listOfSpans):
        self.listofNodes = listofNodes
        self.listOfSupports = listOfSupports
        self.listofpl = listofpl
        self.listofudl = listofudl
        self.listofTMSpan = listofTMSpan
        self.listOfSpans = listOfSpans

    def calculate(self):
        n = len(self.listOfSupports)
        redn_n = n  - 2
        L_matrix = np.zeros((redn_n, redn_n))
        b = []

        L1_matrix = []
        L2_matrix = []
        L1_L2_matrix = []

        if redn_n == 2:
            for i in range(redn_n):
                L1, L2, A1x1, A2x2 = self.listofTMSpan[i].calculate_Ax()
                L1_matrix.append(L1)
                L2_matrix.append(L2)
                L1_L2_matrix.append(2*(L1 + L2))
                b.append(-6*(A1x1/L1 + A2x2/L2))

            np.fill_diagonal(L_matrix[1:], L1_matrix)
            np.fill_diagonal(L_matrix, L1_L2_matrix)
            np.fill_diagonal(L_matrix[:, 1:], L2_matrix)
            L_matrix[1, 0] = L1_matrix[1]

        else:
            for i in range(redn_n):
                L1, L2, A1x1, A2x2 = self.listofTMSpan[i].calculate_Ax()
                L1_matrix.append(L1)
                L2_matrix.append(L2)
                L1_L2_matrix.append(2 * (L1 + L2))
                b.append(-6 * (A1x1 / L1 + A2x2 / L2))

                np.fill_diagonal(L_matrix[1:], L1_matrix)
                np.fill_diagonal(L_matrix, L1_L2_matrix)
                np.fill_diagonal(L_matrix[:, 1:], L2_matrix)

        # print(L_matrix)

        inverse = np.linalg.inv(L_matrix)
        Moments = list(inverse.dot(np.array(b)))
        Moments.insert(0, 0)
        Moments.append(0)

        # # Reactions
        Reactions = [0]
        Reactions = Reactions * len(self.listOfSpans)
        # if redn_n == 2 :
        firstpan = self.listOfSpans[0]
        L = firstpan.length()
        x2 = firstpan.rightSupport.node.x
        if firstpan.listPL:
            load = firstpan.listPL[0]
            P = load.magnitude
            xp = load.node.x
            Ra = ((P * (x2 - xp)) - abs(Moments[1]))/L
            RbL = P - Ra

        elif firstpan.listUDL:
            load = firstpan.listUDL[0]
            w = load.intensity
            Ra = ((w*L**2)/2 - abs(Moments[1]))/L
            RbL = (w*L) - Ra

        Reactions[0] = Ra, RbL


        # Intermediate spans
        for i in range(1, len(self.listOfSpans)-1):
            span = self.listOfSpans[i]
            L = span.length()
            x2 = span.rightSupport.node.x
            if span.listPL:
                load = span.listPL[0]
                P = load.magnitude
                xp = load.node.x
                RbR = (P * (x2 - xp) + abs(Moments[i]) - abs(Moments[i+1])) / L
                RcL = P - RbR

            elif span.listUDL:
                load = span.listPL[0]
                w = load.intensity
                xp = load.node.x
                RbR = ((w * L ** 2) / 2 + abs(Moments[i]) - abs(Moments[i+1])) / L
                RcL = (w * L) - RbR

            Reactions[i] = RbR, RcL

        lastpan = self.listOfSpans[-1]
        L = lastpan.length()
        x2 = lastpan.rightSupport.node.x
        if lastpan.listPL:
            load = lastpan.listPL[0]
            P = load.magnitude
            xp = load.node.x
            Rd = ((P * (x2 - xp)) - abs(Moments[-2]))/L
            RcR = P - Rd

        elif lastpan.listUDL:
            load = lastpan.listUDL[0]
            w = load.intensity
            Rd = ((w*L**2)/2 - abs(Moments[-2]))/L
            RcR = (w*L) - Rd

        Reactions[-1] = RcR, Rd


        return Moments, Reactions



#List of Nodes
A = Node(0, 0)
E = Node(2, 0)
B = Node(6, 0)
F = Node(8, 0)
C = Node(11, 0)
D = Node(15, 0)
H = Node(18, 0)
G = Node(24, 0)

#List of Supports
supportA = Support(A, 'pin')
supportB = Support(B, 'roller')
supportC = Support(C, 'roller')
supportD = Support(D, 'roller')
# supportH = Support(H, 'roller')
# supportG = Support(G, 'roller')

#List of UDL
udl1 = UDL(supportC, supportD, 3)
# udl2 = UDL(supportD, supportH, 3)
# udl3 = UDL(supportH, supportG, 4)


#List of Nodes
ploadE = PointLoad(E, 9)
ploadF = PointLoad(F, 8)


span1 = Span(supportA, supportB, [ploadE], [])
span2 = Span(supportB, supportC, [ploadF], [])
lastpan = Span(supportC, supportD, [], [udl1])
# span4 = Span(supportD, supportH, [], [udl2])
# span5 = Span(supportH, supportG, [], [udl3])

threeMomentSpan1 = TMSpan(span1, span2)
threeMomentSpan2 = TMSpan(span2, lastpan)
# threeMomentSpan3 = TMSpan(span3, span4)
# threeMomentSpan4 =  TMSpan(span4, span5)


solve = Solver([A, B, C, D, E, F, H, G], [supportA, supportB, supportC, supportD],
               [ploadE, ploadF], [udl1], [threeMomentSpan1, threeMomentSpan2], [span1, span2, lastpan])


