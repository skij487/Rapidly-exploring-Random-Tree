import cv2
import random
import numpy as np

coordinates = []
topleft = (0.2, 0.2)
topright = (0.4, 0.2)
bottomleft = (0.2, -0.2)
bottomright = (0.4, -0.2)

class Node:
    def __init__(self, x, y, parent=None):
            self.x = x
            self.y = y
            self.parent = parent

def check_free(img, node):
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    if (node.y >= len(img_gray) or node.x >= len(img_gray[0])):
        return False
    if (img_gray[node.y, node.x] == 255): # 255 = free
        return True
    else:
        return False

def node_dist(qa, qb):
    return np.sqrt((qa.x - qb.x)**2 + (qa.y - qb.y)**2)

def draw_edge(img, node, b=0, g=0, r=255, thinckness=1):
    cv2.circle(img, (node.x, node.y), radius=thinckness, color=(b,g,r), thickness=-1)
    cv2.line(img, (node.x, node.y), (node.parent.x, node.parent.y), (b,g,r), thinckness)
    cv2.imshow("map",img)
    cv2.waitKey(1)

def click_event(event, x, y, flags, params):
    if event == cv2.EVENT_LBUTTONDOWN:
        coordinates.append((x,y))
        if len(coordinates) > 2:
            cv2.circle(img, (x,y), radius=5, color=(255,255,255), thickness=-1)
        else:
            cv2.circle(img, (x,y), radius=5, color=(255,0,0), thickness=-1)
        cv2.imshow('map', img)

def pixel_to_cartesian(img, node):
    unitx = (topright[0] - topleft[0]) / len(img[0])
    unity = (topleft[1] - bottomleft[1]) / len(img)
    x = node.x * unitx + topleft[0]
    y = topleft[1] - node.y * unity
    new_node = Node(x, y, node.parent)
    return new_node

def cartesian_to_pixel(img, node):
    unitx = len(img[0]) / (topright[0] - topleft[0])
    unity = len(img) / (topleft[1] - bottomleft[1])
    x = int((node.x - topleft[0]) * unitx)
    y = int((topleft[1] - node.y) * unity)
    new_node = Node(x, y, node.parent)
    return new_node

def rand_free(img):
    while True:
        # needed to swap x, y because points=(column,row), image = (row,column)
        x = random.randint(0, len(img[0])-1)
        y = random.randint(0, len(img)-1)
        qrand = Node(x, y)
        if(check_free(img, qrand)):
            return qrand

def near_vertex(qrand, tree):
    # loop through T to find nearest
    minlength = np.inf
    min_node = qrand
    for node in tree:
        dist = node_dist(qrand, node)
        if minlength > dist:
            minlength = dist
            min_node = node
    return min_node

def new_step(qnear, qrand, stepsize):
    dist = node_dist(qnear, qrand)
    if dist > stepsize:
        x = int((qrand.x - qnear.x) / dist * stepsize + qnear.x)
        y = int((qrand.y - qnear.y) / dist * stepsize + qnear.y)
    else:
        x = qrand.x
        y = qrand.y
    return Node(x, y, qnear)

def buildrrt(img, root, steps, stepsize):
    tree = [root]
    for i in range(steps):
        occupied = True
        while occupied:
            qrand = rand_free(img) # im cannot be checked by rrt
            qnear = near_vertex(qrand, tree)
            qnew = new_step(qnear, qrand, stepsize)
            if check_free(img, qnew):
                occupied = False
        tree.append(qnew)
        draw_edge(img, qnew)
    return tree

if __name__ == "__main__":
    img_name = input("Image name:\n")
    default_img = cv2.imread('images/' + img_name)
    steps = int(input("Steps:\n"))
    stepsize = int(input("Stepsize:\n"))

    coordinates = []
    loop = True
    while(loop):
        coordinates = []
        img = default_img.copy()
        cv2.imshow('map', img)
        cv2.setMouseCallback('map',click_event)
        cv2.waitKey(0)
        root = Node(coordinates[0][0], coordinates[0][1])
        goal = Node(coordinates[1][0], coordinates[1][1])
        cv2.circle(img, (root.x, root.y), radius=5, color=(255,0,0), thickness=-1)
        cv2.circle(img, (goal.x, goal.y), radius=5, color=(255,0,0), thickness=-1)
        cv2.imshow('map', img)
        tree = buildrrt(img, root, steps, stepsize)
        gnear = near_vertex(goal, tree)
        reverse_mapping = []
        mapping = []
        if (node_dist(gnear, goal) < stepsize):
            goal.parent = gnear
            draw_edge(img, goal)
            reverse_mapping.append(goal)
            next = goal
            while next != root:
                draw_edge(img, next, 0, 255, 0, 2)
                reverse_mapping.append(next.parent)
                next = next.parent
            mapping = reverse_mapping.copy()
            mapping.reverse()
            for node in mapping:
                new_node = pixel_to_cartesian(img, node)
                print(new_node.x, new_node.y)
            cv2.imwrite('output/mapped_' + img_name, img)
        else:
            print("Path not found")
            cv2.imwrite('output/unmapped_' + img_name, img)
        c = cv2.waitKey(0)
        if c == 27:
            loop = False
