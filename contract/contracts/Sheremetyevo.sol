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
    using IterableMapping for IterableMapping.Map;

    address private _server;
    mapping(address => uint256) private _tariffs;
    IterableMapping.Map private _balances;

    modifier only_for_server() {
        require(msg.sender == _server, "Only owner can call this method");
        _;
    }

    constructor() {
        _server = msg.sender;
    }

    function set(address user, uint256 tariff) public only_for_server {
        _tariffs[user] = tariff;
    }

    function setBalance(address user, int256 balance) public only_for_server {
        _balances.set(user, balance);
    }

    function withdraw(address from, address to, uint256 amount) public only_for_server {
        require(_balances.get(from) >= amount, "Balance is not enough");
    }

    function getBalance(address user) external view returns (uint256) {
        return _balances.get(user);
    }

    function getTariff(address user) external view returns (uint256) {
        return _tariffs[user];
    }

    function iterDay() public only_for_server {
        for (uint i = 0; i < _balances.size(); i++) {
            address key = _balances.getKeyAt(i);
            _balances.set(key, _balances.get(key) - _tariffs[key]);
        }
    }

    fallback() external payable {
        _balances.set(msg.sender, _balances.get(msg.sender) + msg.value);
    }
}
