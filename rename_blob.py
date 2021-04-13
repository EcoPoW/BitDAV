
import sys
import os

if __name__ == '__main__':
    for i in '0123456789abcdef':
        for j in '0123456789abcdef':
            for k in '0123456789abcdef':
                os.makedirs('blob/'+i+k+j, exist_ok=True)

                files = os.scandir('blob/'+i+k+j)
                print(i+k+j)

                for f in files:
                    if(len(f.name) == 61):
                        print(f.name, len(f.name))
                        os.rename('blob/'+i+k+j+'/'+f.name, 'blob/'+i+k+j+'/'+i+k+j+f.name)
