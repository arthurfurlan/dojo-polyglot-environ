#!/usr/bin/env lua

-- automatically created by Dojo Polyglot Environ on DATETIME
-- https://github.com/afurlan/dojo-polyglot-environ

CLASSNAME = {}
function CLASSNAME:new()
end

TestCLASSNAME = {}
function TestCLASSNAME:test_new()
    assertEquals(CLASSNAME:new(), nil)
end

require("luaunit")
LuaUnit:run()
