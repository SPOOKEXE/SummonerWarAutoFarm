
local WeightedGraphModule = require(script:WaitForChild('WeightedGraph'))
local AStarPathfinding = require(script:WaitForChild('AStarPathfinding'))

local scaleFactor = 100
local visualY = 10

local RNG = Random.new(3)

--local nodes, edges = WeightedGraphModule.GenerateRandomUndirected( 500, RNG )
local nodes, edges = WeightedGraphModule.GenerateGridUndirected( 60, RNG )
local nodeAdornments, edgeAdornments = WeightedGraphModule.VisualizeGraph( nodes, edges, scaleFactor, visualY )

local function PickRandomNode( nodes, cannot_match )
	local counter = 30
	while counter > 0 do
		counter -= 1
		local randomNode = nodes[RNG:NextInteger(1, #nodes)]
		if randomNode.barrier or randomNode == cannot_match then
			continue
		end
		return randomNode
	end
end

local function FindEdgeAdornment( node, other )
	local key1 = node.id..'_'..other.id
	local key2 = other.id..'_'..node.id
	return edgeAdornments[ key1 ] or edgeAdornments[ key2 ]
end

local function VisualResolvePath(
	nodes : table,
	edges : table,
	start : table,
	goal : table,
	cache : table?
) : table?
	local pathKey = AStarPathfinding.HashPath( start, goal )
	if cache and cache[pathKey] ~= nil then
		return cache[pathKey]
	end

	local frontier = { start }
	local cameFrom = { [start] = false }
	local costTable = { [start] = 1 }

	local activePoint = nil
	local steps = 0
	while #frontier > 0 do 
		if table.find( frontier, goal ) then
			activePoint = goal
			break
		end
		
		activePoint = table.remove(frontier, 1)
		steps += 1

		local neighbours = edges[activePoint]
		for _, point in ipairs( neighbours ) do
			if point.barrier then
				continue
			end
			
			local cost = AStarPathfinding.GetCost(activePoint, point, costTable[point] or point.cost, start, goal )
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
			-- frontier
			if point ~= start and point ~= goal then
				nodeAdornments[point].Color3 = Color3.new(1, 0, 1)
				nodeAdornments[point].Radius = 0.75
			end
		end

		table.sort(frontier, function(pointA, pointB)
			return costTable[pointA] < costTable[pointB]
		end)
		
		if steps % 2 == 0 then
			task.wait()
		end
	end

	if activePoint == goal then 
		local resolvedPath = {}
		local totalCost = 0
		local last = nil
		while activePoint and activePoint ~= start do
			table.insert(resolvedPath, activePoint)
			totalCost += costTable[activePoint]
			activePoint = cameFrom[activePoint]
			-- color
			nodeAdornments[activePoint].Color3 = Color3.fromRGB(255, 238, 0)
			local edge = last and FindEdgeAdornment(activePoint, last)
			if edge then
				edge.Color = ColorSequence.new(Color3.fromRGB(255, 238, 0))
			end
			last = activePoint
			task.wait()
		end
		if cache then
			cache[pathKey] = resolvedPath
		end
		return resolvedPath, steps, totalCost
	end

	return nil, steps, -1
end

local function ResolveRandomPath( nodes, edges )
	
	local startNode = PickRandomNode( nodes, nil )
	assert( startNode, 'Could not find a start node.' )

	local goalNode = PickRandomNode( nodes, startNode )
	assert( goalNode, 'Could not find a goal node.' )

	nodeAdornments[ startNode ].Color3 = Color3.fromRGB(44, 255, 62)
	nodeAdornments[ startNode ].Radius = 1
	nodeAdornments[ goalNode ].Color3 = Color3.fromRGB(255, 85, 0)
	nodeAdornments[ goalNode ].Radius = 1
	
	local path, total_steps, cost = VisualResolvePath(
		nodes,
		edges,
		startNode,
		goalNode,
		nil
	)
	
	warn(path and 'Path was found.' or 'Path could not be found.')
	warn('#PATH: ' .. (path and #path or -1))
	warn('STEPS TAKEN: ' .. total_steps)
	warn('COST: ' .. cost)
	
end

task.wait(1)
while true do
	ResolveRandomPath( nodes, edges )
	task.wait(5)
	WeightedGraphModule.ResetGraphVisual(nodeAdornments, edgeAdornments)
end

