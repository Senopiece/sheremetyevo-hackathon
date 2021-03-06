pragma solidity ^0.7.6;

library IterableMapping {
    // Iterable mapping from address to uint;
    struct Map {
        address[] keys;
        mapping(address => int256) values;
        mapping(address => uint) indexOf;
        mapping(address => bool) inserted;
    }

    function get(Map storage map, address key) public view returns (int256) {
        return map.values[key];
    }

    function getKeyAt(Map storage map, uint index) public view returns (address) {
        return map.keys[index];
    }

    function size(Map storage map) public view returns (uint) {
        return map.keys.length;
    }

    function set(
        Map storage map,
        address key,
        int256 val
    ) public {
        if (map.inserted[key]) {
            map.values[key] = val;
        } else {
            map.inserted[key] = true;
            map.values[key] = val;
            map.indexOf[key] = map.keys.length;
            map.keys.push(key);
        }
    }

    function remove(Map storage map, address key) public {
        if (!map.inserted[key]) {
            return;
        }

        delete map.inserted[key];
        delete map.values[key];

        uint index = map.indexOf[key];
        uint lastIndex = map.keys.length - 1;
        address lastKey = map.keys[lastIndex];

        map.indexOf[lastKey] = index;
        delete map.indexOf[key];

        map.keys[index] = lastKey;
        map.keys.pop();
    }
}

contract Sheremetyevo {
    event tariffChanged(address user, uint256 tariff);
    event payed(address user, uint256 value);
    event withdrawed(address user, uint256 amount);
    event earned(address user, uint256 value); // on server balance increase with amount from user address
    
    using IterableMapping for IterableMapping.Map;

    uint256 last_iter;
    address private _server;
    mapping(address => int256) private _tariffs;
    IterableMapping.Map private _balances;

    modifier only_for_server() {
        require(msg.sender == _server, "Only owner can call this method");
        _;
    }

    constructor() {
        _server = msg.sender;
        last_iter = block.timestamp;
    }

    function set(address user, int256 tariff) public only_for_server {
        require(tariff > 0, "Tariff must be greater than zero");
        _tariffs[user] = tariff;
        emit tariffChanged(user, uint256(tariff));
    }

    function withdraw(address user, address to, int256 amount) public only_for_server {
        require(amount > 0, "Amount must be greater than zero");
        require(_balances.get(user) >= amount, "Balance is not enough");
        payable(to).send(uint256(amount));
        _balances.set(user,  _balances.get(user) - amount);
        emit withdrawed(user, uint256(amount));
    }

    function getBalance(address user) external view returns (int256) {
        return _balances.get(user);
    }

    function getTariff(address user) external view returns (int256) {
        return _tariffs[user];
    }

    function iterDay() public only_for_server {
        require(block.timestamp > last_iter + 10 seconds, "too early");
        last_iter = block.timestamp;
        for (uint i = 0; i < _balances.size(); i++) {
            address key = _balances.getKeyAt(i);
            int256 balance = _balances.get(key);
            int256 payment = _tariffs[key];
            if (balance > 0)
            {
                if (balance >= payment)
                {
                    _balances.set(_server, _balances.get(_server) + payment);
                    emit earned(key, uint256(payment));
                }
                else
                {
                    _balances.set(_server, _balances.get(_server) + balance);
                    emit earned(key, uint256(balance));
                }
            }
            _balances.set(key, balance - payment);
        }
    }

    function _pay(address user) internal {
        require(user != _server, "Server souldn't pay to contract");
        emit payed(user, msg.value);
        int256 balance = _balances.get(user);
        int256 value = int256(msg.value);
        if (balance < 0)
        {
            int256 remains = -balance;
            if (remains >= value)
            {
                _balances.set(_server, _balances.get(_server) + value);
                emit earned(user, uint256(value));
            }
            else
            {
                _balances.set(_server, _balances.get(_server) + remains);
                emit earned(user, uint256(remains));
            }
        }
        _balances.set(user, balance + value);
    }

    function pay(address user) external payable {
        _pay(user);
    }

    fallback() external payable {
        _pay(msg.sender);
    }
}
