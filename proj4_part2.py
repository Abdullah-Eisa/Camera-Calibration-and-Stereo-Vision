import warnings
import numpy as np
import os
import argparse
from student import (calculate_projection_matrix, compute_camera_center)
from helpers import (evaluate_points, visualize_points, plot3dview)
import cv2
import numpy as np
import os
import glob


####################################################################################

#Calculate the projection matrix given corresponding 2D and 3D points

def camera_calibration(images_dir):
    '''
    input: path
    
    output: M ,objpoints, imgpoints
    
    
    '''
    print("-----/-*/-//*///////////////-------------------")

    # Defining the dimensions of checkerboard
    CHECKERBOARD = (7,7)
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

    # Creating vector to store vectors of 3D points for each checkerboard image
    objpoints = []
    # Creating vector to store vectors of 2D points for each checkerboard image
    imgpoints = [] 


    # Defining the world coordinates for 3D points
    objp = np.zeros((1, CHECKERBOARD[0]*CHECKERBOARD[1], 3), np.float32)
    objp[0,:,:2] = np.mgrid[0:CHECKERBOARD[0], 0:CHECKERBOARD[1]].T.reshape(-1, 2)
    prev_img_shape = None

    # Extracting path of individual image stored in a given directory
    # images = glob.glob('./images/*.jpg')
    images = glob.glob(images_dir+'/*.jpeg')
    print(len(images))
    print("path---- ",images_dir )
    gray=[]
    for fname in images:
        img = cv2.imread(fname)
        gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        #cv2.imshow('gray',gray)
        # Find the chess board corners
        # If desired number of corners are found in the image then ret = true
        ret, corners = cv2.findChessboardCorners(gray, CHECKERBOARD, cv2.CALIB_CB_ADAPTIVE_THRESH+cv2.CALIB_CB_FAST_CHECK+cv2.CALIB_CB_NORMALIZE_IMAGE)
        corners = np.array([corner for [corner] in corners])

        #print("ret\n",ret)
        #print("corners\n",corners)

        """
        If desired number of corner are detected,
        we refine the pixel coordinates and display 
        them on the images of checker board
        """
        if ret == True:

            print("------- in ret=true")
            objpoints.append(objp)
            # refining pixel coordinates for given 2d points.
            corners2 = cv2.cornerSubPix(gray,corners,(11,11),(-1,-1),criteria)

            imgpoints.append(corners2)
            print("---if-imgpoints------ ", np.shape(imgpoints))

            # Draw and display the corners
            img = cv2.drawChessboardCorners(img, CHECKERBOARD, corners2,ret)

        break
        #cv2.imshow('img',img)
        #cv2.waitKey(0)

    cv2.destroyAllWindows()

    #h,w = img.shape[:2]

    """
    Performing camera calibration by 
    passing the value of known 3D points (objpoints)
    and corresponding pixel coordinates of the 
    detected corners (imgpoints)
    """

    
    print("----gray------ ", gray.shape)
    '''
    print("----imgpoints------ ", np.shape(imgpoints))
    print("----objpoints------ ", np.shape(objpoints))
    print("---------objpoints------ ",objpoints)
    '''
    print("---------imgpoints------ ",imgpoints)
    print("----imgpoints------ ", np.shape(imgpoints))

    imgpoints=np.array(imgpoints)
    imgpoints=np.reshape(imgpoints,(49,2))

    objpoints=np.array(objpoints)
    objpoints=np.reshape(objpoints,(49,3))
    print("----imgpoints------ ", np.shape(imgpoints))


#    ret, K, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1],None,None)
    #ret, K, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape(),None,None)

    ret, K, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, np.shape(gray)[::-1],None,None)

    
    
    R = cv2.Rodrigues(rvecs[0])[0]
    t = tvecs[0]
    temp=np.concatenate((R,t),axis=1)
    
    M = np.dot(K,temp)
    
    '''
    R = cv2.Rodrigues(rvecs[0])[0]
t = tvecs[0]
Rt = np.concatenate([R,t], axis=-1) # [R|t]
P = np.matmul(mtx,Rt) # A[R|t]
    '''
    

    return M,objpoints, imgpoints,K




data_dir = os.path.dirname(__file__) + '../data/'

images_dir_r=data_dir+'/right'
images_dir_l=data_dir+'/left'

#Validate the computed projection matrix as done in PART I

M_r,objpoints_r, imgpoints_r,K_dash=camera_calibration(images_dir_r)
M_l,objpoints_l, imgpoints_l,K=camera_calibration(images_dir_l)


print("objpoints_r--------",len(objpoints_r))
print("imgpoints_r--------",len(imgpoints_r))

M_r_0=calculate_projection_matrix(imgpoints_r,objpoints_r)
M_l_0=calculate_projection_matrix(imgpoints_l,objpoints_l)

print("the difference between calibrated and implemented  right projection matrix M_r= ",M_r-M_r_0)
print("the difference between calibrated and implemented  left projection matrix M_l= ",M_l-M_l_0)

# evaluate points
[Projected_2D_Pts_l, Residual_l] = evaluate_points( M_l, imgpoints_l,objpoints_l) 
[Projected_2D_Pts_r, Residual_r] = evaluate_points( M_r, imgpoints_r,objpoints_r)

#Calculate the camera center using the M found from previous step
Center_l = compute_camera_center(M_l)
Center_r = compute_camera_center(M_r)

#compute the fundamental matrix
# F=
# F, mask = cv2.findFundamentalMat(img1_points, img2_points, cv2.FM_RANSAC)
S=cv2.stereoCalibrate(objpoints_r, imgpoints_r,imgpoints_l)    # objpoints_r may cause errors ?
E=S[:-2]


# print("Camera matrix : \n")
# print(mtx)
# print("dist : \n")
# print(dist)
# print("rvecs : \n")
# print(rvecs)
# print("tvecs : \n")
# print(tvecs)



# visualize points
# visualize_points(Points_2D_l,Projected_2D_Pts_l)
# visualize_points(Points_2D_r,Projected_2D_Pts_r)
