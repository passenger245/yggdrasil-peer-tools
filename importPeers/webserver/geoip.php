<?php
require_once 'vendor/autoload.php';
use GeoIp2\Database\Reader;


class Ygg_Geo
{

    var $_reader;
    var $_peerData;


    // https://stackoverflow.com/questions/10053358/measuring-the-distance-between-two-coordinates-in-php
    private function vincentyGreatCircleDistance(
        $latitudeFrom, $longitudeFrom, $latitudeTo, $longitudeTo, $earthRadius = 6371000)
    {
        $latFrom = deg2rad($latitudeFrom);
        $lonFrom = deg2rad($longitudeFrom);
        $latTo = deg2rad($latitudeTo);
        $lonTo = deg2rad($longitudeTo);

        $lonDelta = $lonTo - $lonFrom;
        $a = pow(cos($latTo) * sin($lonDelta), 2) +
            pow(cos($latFrom) * sin($latTo) - sin($latFrom) * cos($latTo) * cos($lonDelta), 2);
        $b = sin($latFrom) * sin($latTo) + cos($latFrom) * cos($latTo) * cos($lonDelta);

        $angle = atan2(sqrt($a), $b);
        return $angle * $earthRadius;
    }


    private function getLatLng($ip)
    {
        if (!isset($this->_reader)) $this->_reader = $this->getReader();
        if ($ip == "127.0.0.1") $ip = "1.1.1.1";
        $record = $this->_reader->city($ip);
        return array(
            "lat" => $record->location->latitude,
            "long" => $record->location->longitude
        );
    }

    private function getReader()
    {
        $reader = new Reader('GeoLite2-City.mmdb');
        return $reader;
    }

    public function getDistance($peerIP)
    {
        $clientLoc = $this->getLatLng($_SERVER["HTTP_X_FORWARDED_FOR"]);
        $peerLoc = $this->getLatLng($peerIP);
        return
            $this->vincentyGreatCircleDistance($clientLoc["lat"], $clientLoc["long"],
                $peerLoc["lat"], $peerLoc["long"]);
    }
}

?>
