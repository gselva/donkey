'''
file utilities
'''
import os
import glob

def most_recent_file(dir_path, ext=''):
    '''
    return the most recent file given a directory path and extension
    '''
    query = dir_path + '/*' + ext
    newest = min(glob.iglob(query), key=os.path.getctime)
    return newest


def make_dir(path):
    real_path = os.path.expanduser(path)
    if not os.path.exists(real_path):
        os.makedirs(real_path)
    return real_path


def parse_file_name(f):
    f = f.split('/')[-1]
    f = f.split('.')[0]
    f = f.split('_')
    speed = int(f[3])
    angle = int(f[5])
    #msecs = int(f[7])
    return angle, speed


def filter_session(session_path, speed_threshold = 200):
    """
    Get the paths to session images that are likely not before or after
    a crash. 
    """
    imgs = os.listdir(session_path)
    imgs.sort()

    split_imgs = [parse_file_name(i) for i in imgs]

    keep_index = [0 for _ in imgs]

    for i, x in enumerate(imgs):
        #remove images with speed < 200
        if split_imgs[i][1] < speed_threshold:
            keep_index[i]=0
        #remove the first and last 60 frames
        elif i < 60 or i > len(imgs) - 60:
            keep_index[i]=0
        else:
            keep_index[i]=1

    past_removed = 0
    for i, x in enumerate(imgs):
        #remove the 20 frames before an images with speed <threshold
        if 0 in keep_index[i: i+20]: 
            if keep_index[i] != 0:
                past_removed += 1
                keep_index[i]=0

    future_removed = 0
    for i, x in reversed(list(enumerate(imgs))):
        #remove the 20 frames after an image with speed <threshold
        if 0 in keep_index[i-20: i]: 
            if keep_index[i] != 0:
                future_removed += 1
                keep_index[i]=0

    print('total images: %s   kept:%s' %(len(imgs), sum(keep_index)))
    
    filtered_imgs = [img for i, img in enumerate(imgs) if keep_index[i] ==1 ]
    filtered_img_paths = [os.path.join(session_path, i) for i in filtered_imgs]
    return filtered_img_paths



def variant_generator(img_paths, variant_funcs = None):

    if variant_funcs == None:
        variants_funcs = [
             {'func': lambda x: x, 'args': {}},
             {'func': exposure.adjust_sigmoid, 'args': {'cutoff':.4, 'gain':7}}
            ]

    def orient(arr, flip=False):
        if flip == False:
            return arr
        else: 
            return np.fliplr(arr)
    
    while True:
        for flip in [True, False]:
            for v in variants:
                for img_path in img_paths:
                    img = Image.open(img_path)
                    img = np.array(img)
                    img =  v['func'](img, **v['args'])
                    img = orient(img, flip=flip)
                    x = arr.transpose(2, 0, 1)
                    angle, speed = parse_file_name(img_path)
                    if flip == True: 
                        angle = -angle #reverse stering angle
                    y = np.array([angle, speed])
                    x = np.expand_dims(x, axis=0)
                    y = y.reshape(1, 2)
                    yield (x, y)