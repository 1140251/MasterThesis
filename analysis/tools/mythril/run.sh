
FILENAME=$1

for c in FILEPath; 
do 
        path_contract=$(echo "$1" | sed -e 's/^\///')
        myth analyze $path_contract
done