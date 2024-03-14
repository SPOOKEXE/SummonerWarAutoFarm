
-- // Module // --
local Module = {}

function Module.GetNodeDistance( node_a : table, node_b : table ) : number
	local dx = node_b.position.X - node_a.position.X
	local dy = node_b.position.Y - node_a.position.Y
	return (dx * dx) + (dy * dy)
end

function Module.GetEdgeDistance( node_a, node_b ) : number
	return (node_a.cost + node_b.cost) / 2
end

function Module.GetCost( activePoint : table, neighbour : table, current : number, start : table, goal : table ) : number
	return
		current
		+ Module.GetEdgeDistance(activePoint, neighbour) -- edge distance
		+ Module.GetNodeDistance(neighbour, start) -- goal to start
		+ Module.GetNodeDistance(neighbour, goal) -- goal to end
end

function Module.HashPath( start : table, goal : table ) : string
	return tostring(start.position)..'|'..tostring(goal.position)
end

--[[function Module.SolveFullPath(
	nodes : table,
	edges : table,
	start : table,
	goal : table,
	cache : table?
) : table?
	local pathKey = Module.HashPath( start, goal )
	if cache and cache[pathKey] ~= nil then
		return cache[pathKey]
	end
	
	local frontier = { start }
	local cameFrom = { [start] = false }
	local costTable = { [start] = 1 }
	
	local activePoint = nil
	while #frontier > 0 do 
		if table.find(frontier, goal) then
			activePoint = goal
			break
		end

		activePoint = table.remove(frontier, 1)
		for _, point in ipairs( edges[activePoint] ) do 
			local cost = Module.GetCost(activePoint, point, costTable[point] or 1, start, goal )
			if cameFrom[point] then 
				if cost < costTable[point] then
					costTable[point] = cost
					cameFrom[point] = activePoint
					table.insert(frontier, 1, point)
				end
			else
				costTable[point] = cost
				cameFrom[point] = activePoint
				table.insert(frontier, point)
			end
		end

		table.sort(frontier, function(pointA, pointB)
			return costTable[pointA] < costTable[pointB]
		end)
	end

	if activePoint == goal then 
		local resolvedPath = {}
		while activePoint and activePoint ~= start do
			table.insert(resolvedPath, activePoint)
			activePoint = cameFrom[activePoint]
		end
		if cache then
			cache[pathKey] = resolvedPath
		end
		return resolvedPath
	end
	
	return nil
end]]

return Module
