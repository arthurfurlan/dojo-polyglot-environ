<?php
require_once 'PHPUnit/Framework.php';

class CLASSNAME {
    function __construct() {
    } 
}

class CLASSNAME_Test extends PHPUnit_Framework_TestCase {
    public function testConstruct() {
        $this->assertNotEquals(new CLASSNAME, null);
    }
}
?>
