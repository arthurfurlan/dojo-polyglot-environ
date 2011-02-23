#!/usr/bin/env ruby

require "test/unit"

class CLASSNAME
    def initialize
    end
end

class TestCLASSNAME < Test::Unit::TestCase
    def test_initialize
        assert_not_nil(CLASSNAME.new)
    end
end
