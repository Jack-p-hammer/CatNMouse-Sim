import numpy as np 
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import random
import time

N = 100000
start = time.time()

class Thing():
    list1 = []
    def __init__(self, x_0, y_0, dt = .01):
        self.x = x_0
        self.y = y_0
        self.dt = dt
        self.pos = np.zeros((N,2))
        self.pos[0] = [self.x, self.y]
        self.count = 1
        Thing.list1.append(self)
    
    def update(self, u, t):
        """Takes in current state u vector and updates based on evalf funciton, increments counter, appends to the states"""
        dF = self.evalf(u, t)
        dt = self.dt
        self.x += dt*dF[0]
        self.y += dt*dF[1]        
        self.pos[self.count] = [self.x, self.y]
        self.count += 1
        
    def evalf(self, u, t):
        NotImplementedError
    
    def get_pos(self):
        return self.pos[self.count-1]
    
    def get_states(self):
        return self.pos

class Mouse(Thing):
    listMouse = []
    def __init__(self, x_0, y_0):
        super().__init__(x_0, y_0)
        Mouse.listMouse.append(self)
        
    def evalf(self, u, t):
        x = u[0]
        y = u[1]
        dx = 1
        dy = 2*np.cos(1000*t)
        return [dx, dy]
    
class Cat(Thing):
    listCat = []
    def __init__(self, x_0, y_0, chasing):
        super().__init__(x_0, y_0)
        self.chasing = chasing
        self.I_total = [0,0]
        self.D_total = [[0,0], # x's
                        [0,0]] # y's
        self.P_coeff = 4
        self.I_coeff = 1.5
        self.D_coeff = .075
        
        Cat.listCat.append(self)
        
    def evalf(self, u, t):
        dx, dy = self.get_distance(False)
        error = self.get_distance(True)
        dx *= self.P_coeff
        dy *= self.P_coeff
        
        self.integrate()
        dx += self.I_coeff*self.I_total[0]
        dy += self.I_coeff*self.I_total[1]
        
        Dx, Dy = self.derivative()
        dx += self.D_coeff*Dx
        dy += self.D_coeff*Dy
        
        max_c = 25
        if dx > max_c:
            dx = max_c
        if dx < -max_c:
            dx = -max_c
        if dy > max_c:
            dy = max_c
        if dy < -max_c:
            dy = -max_c
   
        return [dx, dy]
    
    def integrate(self):
        diffx, diffy = self.get_distance(False)
        self.I_total[0] += diffx*self.dt
        self.I_total[1] += diffy*self.dt
        
    def derivative(self):
        self.D_total[0][0] = self.D_total[0][1]
        self.D_total[0][1] = self.get_distance(False)[0]
        dX = self.D_total[0][1] - self.D_total[0][0]
        dXdt = dX/self.dt
        
        self.D_total[1][0] = self.D_total[1][1]
        self.D_total[1][1] = self.get_distance(False)[1] 
        dY = self.D_total[1][1] - self.D_total[1][0]
        dYdt = dY/self.dt
        return [dXdt, dYdt]
        
    def get_distance(self, totalDistance = True):
        """If totalDistance is true, return sqrt of sqrare of components, otherwise, return components in x,y,z format"""
        Mx, My = self.chasing.get_pos()
        Sx, Sy = self.get_pos()
        if totalDistance == True:
            return np.sqrt(abs((Mx - Sx)**2 + (My - Sy)**2))
        else:
            Dx = Mx - Sx
            Dy = My - Sy
            return Dx, Dy

fig, ax = plt.subplots()
Rus = Mouse(0,0)
x = random.uniform(-5,5)
y = random.uniform(-5,5)
Am = Cat(x,y, Rus)
times = np.linspace(0,10,N)
lims = 5
distances = []
Intercepted = False

def animate(i):
    Rus.update(Rus.get_pos(), times[i])
    Am.update(Am.get_pos(), times[i])
    ax.clear()
    ax.set_ylim([-lims,lims])
    ax.set_xlim([-lims,lims])

    Adis = Am.get_distance(True)
    distances.append(Adis)
            
    idx = Rus.count    
    ax.plot(Rus.get_states()[:idx,0], Rus.get_states()[:idx,1], color = "red")
    ax.plot(Am.get_states()[:idx,0], Am.get_states()[:idx,1], color = "blue")
    ax.grid(True)
    
    Rlist  = Rus.get_pos()
    Alist  = Am.get_pos()
    check = np.isclose(a = Rlist, b = Alist, atol = .05, rtol = 0)

    print(f"Rus: {Rlist}, Am: {Alist}, check: {check}")
    
    if idx == 500:
        plt.close()

    if check[0] and check[1]:
        Intercepted = True
        plt.close()

ani = FuncAnimation(fig, animate, frames=5000, interval= 1, repeat = False)

plt.show()
end = time.time()
timed = end - start

print("----------------------------------------")
if not Intercepted:
    print(f"Am intercepted Rus at time: {timed}")
else:
    print(f"Not intercepted")
print(f"Closest is {min(distances)}")