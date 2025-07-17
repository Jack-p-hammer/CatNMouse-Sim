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
        if dF is None:
            return
        dt = self.dt
        self.x += dt*dF[0]
        self.y += dt*dF[1]        
        self.pos[self.count] = [self.x, self.y]
        self.count += 1
        
    def evalf(self, u, t):
        raise NotImplementedError
    
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

        self.I_windup_limit = 20
        self.actuator_limit = 25

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
        
        max_c = self.actuator_limit
        # Limit the actuator output
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
        # Wind up limitations
        self.I_total[0] = np.clip(self.I_total[0], -self.I_windup_limit, self.I_windup_limit)
        self.I_total[1] = np.clip(self.I_total[1], -self.I_windup_limit, self.I_windup_limit)

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
    
    def get_pid_values(self):
        """Return current PID values for display"""
        diffx, diffy = self.get_distance(False)
        P_x = diffx * self.P_coeff
        P_y = diffy * self.P_coeff
        I_x = self.I_coeff * self.I_total[0]
        I_y = self.I_coeff * self.I_total[1]
        Dx, Dy = self.derivative()
        D_x = self.D_coeff * Dx
        D_y = self.D_coeff * Dy
        return P_x, P_y, I_x, I_y, D_x, D_y
    
    def get_actuator_values(self):
        """Return current actuator/control effort values"""
        diffx, diffy = self.get_distance(False)
        dx = diffx * self.P_coeff
        dy = diffy * self.P_coeff
        
        dx += self.I_coeff * self.I_total[0]
        dy += self.I_coeff * self.I_total[1]
        
        Dx, Dy = self.derivative()
        dx += self.D_coeff * Dx
        dy += self.D_coeff * Dy
        
        # Apply actuator limits (same as in evalf method)
        max_c = self.actuator_limit
        if dx > max_c:
            dx = max_c
        if dx < -max_c:
            dx = -max_c
        if dy > max_c:
            dy = max_c
        if dy < -max_c:
            dy = -max_c
            
        return dx, dy

fig, ax = plt.subplots(figsize=(10, 8))
plt.ion()  # Turn on interactive mode
Rus = Mouse(0,0)
x = random.uniform(-5,5)
y = random.uniform(-5,5)
Am = Cat(x,y, Rus)
times = np.linspace(0,10,N)
lims = 5
distances = []
Intercepted = False

def update(i):
    global Intercepted
    
    # Only update positions if not intercepted
    if not Intercepted:
        Rus.update(Rus.get_pos(), times[i])
        Am.update(Am.get_pos(), times[i])
    
    ax.clear()
    ax.set_ylim(-lims, lims)
    ax.set_xlim(-lims, lims)

    Adis = Am.get_distance(True)
    if not Intercepted:
        distances.append(Adis)
    else:
        Adis = "Intercepted"
            
    idx = Rus.count    
    mouse_line = ax.plot(Rus.get_states()[:idx,0], Rus.get_states()[:idx,1], color = "red", label="Mouse")
    cat_line = ax.plot(Am.get_states()[:idx,0], Am.get_states()[:idx,1], color = "blue", label="Cat")

    ax.grid(True)
    ax.legend()
    
    # Add PID values display
    P_x, P_y, I_x, I_y, D_x, D_y = Am.get_pid_values()
    act_x, act_y = Am.get_actuator_values()
    pid_text = f"""PID Values:
P: ({P_x:.2f}, {P_y:.2f})
I: ({I_x:.2f}, {I_y:.2f})
D: ({D_x:.2f}, {D_y:.2f})

Actuator Output:
X: {act_x:.2f}
Y: {act_y:.2f}

Coefficients:
P: {Am.P_coeff}, I: {Am.I_coeff}, D: {Am.D_coeff}

Limits:
I Windup: ±{Am.I_windup_limit}
Actuator: ±{Am.actuator_limit}

Distance: {Adis:.3f}
"""
    
    # Add interception message if intercepted
    if Intercepted:
        pid_text += "\n\nINTERCEPTED!"
    
    text_box = ax.text(0.02, 0.98, pid_text, transform=ax.transAxes, 
            verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8),
            fontsize=9, fontfamily='monospace')
    
    Rlist  = Rus.get_pos()
    Alist  = Am.get_pos()
    check = np.isclose(a = Rlist, b = Alist, atol = .05, rtol = 0)
    if check[0] and check[1] and not Intercepted:
        Intercepted = True
        print("Mouse intercepted!")
    
    plt.draw()
    plt.pause(0.01) # Small pause for smooth animation

# Animation loop
i = 0
while i < N and not Intercepted:
    if not plt.fignum_exists(fig.number):
        print("Window closed by user.")
        break
    update(i)
    i += 1

plt.ioff()  # Turn off interactive mode
plt.show(block=True)  # Show final result
end = time.time()
timed = end - start

print("\n\n\n\n\n\n\n\n\n----------------------------------------\n")
if Intercepted:
    print(f"Am intercepted Rus at time: {timed}")
else:
    print(f"Not intercepted")
print(f"Closest is {min(distances)}")