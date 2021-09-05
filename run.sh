export PYTHONPATH=$(pwd):$PYTHONPATH
cd streamed-payment
brownie compile
cp build/contracts/* ../web/static/js/abi
cd ../web
python3 __init__.py
