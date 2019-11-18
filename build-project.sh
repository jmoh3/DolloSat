THREADS="${1:-1}"

echo "Building z3"
cd z3
git checkout 9635ddd8fceb6bdde7dc7725e696e6c123af22f4
cp ../quicksampler/check/sat_params.pyg src/sat/sat_params.pyg
cp ../quicksampler/check/dimacs.cpp src/sat/dimacs.cpp
cp ../quicksampler/check/dimacs_frontend.cpp src/shell/dimacs_frontend.cpp
python scripts/mk_make.py
cd build
make -j $THREADS
sudo make install
cd ../..

echo "Building quicksampler"
cd quicksampler
make -j $THREADS
cd ..

echo "Building unigen"
cd unigen/ugen2
make -f Makefile.cvs
mkdir build
cd build
../configure
make -j $THREADS
./unigen -h
cd ..

echo "Done"