<?php

require_once("geoip.php");

class Ygg_Index extends Ygg_Geo {
    var $_geo;
    var $_arguments;
    var $_allowedvars;
    var $_maxPeers;
    function __construct() {
        $this->_arguments = array();
        $this->_allowedvars = array(
            "give_ipv4","give_ipv6","max_results","geo_nearby","limit_continent","output","randomize");

    }

    private function getPeerData() {
        $this->_peerData = json_decode(
                file_get_contents(
                        'https://api.yggdrasil.icu/peers.json')
                ,true
            );
    }

    private function getPeers() {

        if (isset($this->_arguments["geo_nearby"])) {
            $peersIPs = $this->getNearbyPeers();
        } else {
            $peersIPs = array_keys($this->_peerData);
        }

        $count = 0;

        $rtr = array();
        foreach($peersIPs as $peerIP) {
            if ($this->_peerData[$peerIP]["is_ipv4"] && isset($this->_arguments["give_ipv4"])) {
                $rtr[] = $peerIP;
                $count +=1;
            }
            if ($this->_peerData[$peerIP]["is_ipv6"] && isset($this->_arguments["give_ipv6"])) {
                $rtr[] = $peerIP;
                $count +=1;
            }
            if ($count == $this->_maxPeers) break;
        }

        return $rtr;
    }

    private function getNearbyPeers() {
        $peers = array();


        foreach ($this->_peerData as $peer => $values) {
            $distance = $this->getDistance($peer);
            $peers[$peer] = $distance;

        }
        asort($peers);

        return array_keys($peers);
    }

    function parseRequest($httpGet) {
        foreach($this->_allowedvars as $key) {
            if (isset($httpGet[$key])) {
                $this->_arguments[$key] = $httpGet[$key];
            }
        }


        $this->_maxPeers = 5;
        if (isset($this->_arguments["max_results"])) {
            if (is_numeric($this->_arguments["max_results"])) {
                $this->_maxPeers = $this->_arguments["max_results"];
            }
        }
    }

    private function render_raw() {
        $out = array();
        foreach($this->getPeers() as $peerIP) {
            $out[] = sprintf("tcp://%s:%s", $peerIP, $this->_peerData[$peerIP]["port"]);
        }
        echo join("\r\n", $out);
    }

    public function render($httpGet) {
        $this->parseRequest($httpGet);
        $this->getPeerData();
        if ($this->_arguments["output"] == "raw") {
            return $this->render_raw();
        }
    }

}

$ygg = new Ygg_Index();
$ygg->render($_GET);


?>