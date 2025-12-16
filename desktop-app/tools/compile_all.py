import py_compile
import glob

files = glob.glob('**/*.py', recursive=True)
errs = 0
for f in files:
    try:
        py_compile.compile(f, doraise=True)
    except Exception as e:
        print('ERR', f, e)
        errs += 1
print('Done', len(files), 'files, errors:', errs)
