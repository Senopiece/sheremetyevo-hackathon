export PYTHONPATH=$(pwd):$PYTHONPATH
brownie compile
cp -r streamed-payment/build/contracts web/static/js/abi
cd web
python3 __init__.py
