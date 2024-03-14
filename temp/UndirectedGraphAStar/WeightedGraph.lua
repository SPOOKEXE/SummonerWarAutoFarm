
local Terrain = workspace:WaitForChild('Terrain')

local baseAdornment = Instance.new('SphereHandleAdornment')
baseAdornment.Radius = 0.5
baseAdornment.Color3 = Color3.fromRGB(0, 255, 238)
baseAdornment.Visible = true
baseAdornment.Transparency = 0
baseAdornment.Adornee = Terrain

local baseEdgeBeam = Instance.new('Beam')
baseEdgeBeam.Color = ColorSequence.new( Color3.new(1,1,1) )
baseEdgeBeam.FaceCamera = true
baseEdgeBeam.LightEmission = 0
baseEdgeBeam.LightInfluence = 0
baseEdgeBeam.Transparency = NumberSequence.new(0)
baseEdgeBeam.Segments = 1
baseEdgeBeam.Width0 = 0.1
baseEdgeBeam.Width1 = 0.1

-- // Module // --
local Module = {}

function Module.GenerateGridUndirected( width, RNG )
	
	local map2d = {}
	local links = {}
	local nodes = {}
	
	local counter = 0
	for x = 1, width do
		map2d[x] = {}
		for y = 1, width do
			local node = {
				id = counter,
				position = Vector2.new( x / 10, y / 10 ),
				cost = RNG:NextInteger(1, 5),
				barrier = RNG:NextInteger(1, 4) == 1,
			}
			map2d[x][y] = node
			table.insert(nodes, node)
			counter += 1
		end
	end
	
	for x, t in ipairs( map2d ) do
		for y, node in ipairs( t ) do
			
			local neighbours = {}
			
			local function appendIfExist(nx, ny)
				local node = map2d[nx] and map2d[nx][ny]
				if node then
					table.insert(neighbours, node)
				end 
			end
			
			appendIfExist(x-1, y)
			appendIfExist(x+1, y)
			appendIfExist(x, y-1)
			appendIfExist(x, y+1)
			
			--[[for xi = -1, 1 do
				local horiz = map2d[ x + xi ]
				if not horiz then
					continue
				end
				for yi = -1, 1 do
					if math.sign(xi) == math.sign(yi) then
						continue
					end
					if horiz[ y + yi ] then
						table.insert( neighbours, horiz[ y + yi ] )
					end
				end
			end]]

			links[node] = neighbours
			
		end
	end
	
	return nodes, links
	
end

function Module.GenerateRandomUndirected( number_of_nodes : number, RNG : Random? )
	RNG = RNG or Random.new()

	local max_neighbours = 5
	local min_neighbours = 5
	local precision = 1e3
	
	-- generate a bunch of randomly placed nodes
	local nodes = {}
	for i = 1, number_of_nodes do
		local rnd = Vector2.new( RNG:NextInteger(-precision, precision)/precision, RNG:NextInteger(-precision, precision)/precision )
		table.insert(nodes, {
			id = i,
			position = rnd,
			cost = RNG:NextInteger(1, 5),
			barrier = RNG:NextInteger(1, 4) == 1,
		})
	end
	
	-- use two mappings to make sure no dupe links exist
	local links = {}
	
	for index, node in ipairs( nodes ) do
		
		local sortedNeighbours = table.clone(nodes)
		table.sort(sortedNeighbours, function(a, b)
			return (node.position - a.position).Magnitude < (node.position - b.position).Magnitude
		end)
		
		-- get the neighbours
		local neighbours = {}
		local totalAmount = RNG:NextInteger( min_neighbours, max_neighbours )
		for index = 1, totalAmount do
			if not table.find( neighbours, sortedNeighbours[index] ) then
				table.insert( neighbours, sortedNeighbours[index] )
			end
		end
		links[node] = neighbours
		
		-- for each neighbor, append the current node if its not in the neighbour list already.
		for _, otherNode in ipairs( neighbours ) do
			if not links[otherNode] then
				links[otherNode] = { }
			end
			local t = links[otherNode]
			if not table.find( t, node ) then
				table.insert( t, node )
			end
		end
		
	end
	
	return nodes, links
end

function Module.ResetGraphVisual( nodeAdornments, edgeAdornments )
	for node, adornment in pairs( nodeAdornments ) do
		adornment.Color3 = node.barrier and Color3.new(1, 0, 0) or baseAdornment.Color3
	end
	for node, adornment in pairs( edgeAdornments ) do
		if adornment:GetAttribute('barrier') then
			adornment.Color = ColorSequence.new(Color3.new(1,0,0))
		else
			adornment.Color = ColorSequence.new(Color3.new(1,1,1):Lerp(Color3.new(), 1-adornment:GetAttribute('alpha')))
		end
	end
end

function Module.VisualizeGraph( nodes, edges, scaleFactor, visualY )
	
	local nodeAdornments = {}

	for i, node in ipairs( nodes ) do
		local scaledPosition = node.position * scaleFactor

		local sphereAdornment = baseAdornment:Clone()
		sphereAdornment.CFrame = CFrame.new( scaledPosition.X, visualY, scaledPosition.Y )
		if node.barrier then
			sphereAdornment.Color3 = Color3.new(1, 0, 0)
		end
		sphereAdornment.Parent = Terrain

		nodeAdornments[node] = sphereAdornment
		
		--[[if i%5 == 0 then
			task.wait()
		end]]
	end

	local edgeAdornments = {}
	for i, node in ipairs( nodes ) do
		for i2, neighbour in ipairs( edges[node] ) do
			if i == i2 then
				continue -- same node
			end

			local key1 = node.id..'_'..neighbour.id
			local key2 = neighbour.id..'_'..node.id

			local adornment = edgeAdornments[ key1 ] or edgeAdornments[ key2 ]
			if adornment then
				continue -- adornment between the two nodes already exist
			end

			local scaledNodePosition = node.position * scaleFactor
			local scaledNeighbourPosition = neighbour.position * scaleFactor

			local att0 = Instance.new('Attachment')
			att0.Position = Vector3.new( scaledNodePosition.X, 10, scaledNodePosition.Y )
			att0.Parent = Terrain

			local att1 = Instance.new('Attachment')
			att1.Position = Vector3.new( scaledNeighbourPosition.X, 10, scaledNeighbourPosition.Y )
			att1.Parent = Terrain

			local edgeBeam = baseEdgeBeam:Clone()
			
			local isbarrier = node.barrier or neighbour.barrier
			if isbarrier then
				edgeBeam:SetAttribute('barrier', isbarrier)
				edgeBeam.Color = ColorSequence.new(Color3.new(1,0,0))
			else
				local alpha = ((node.cost + neighbour.cost) / 2) / 5
				edgeBeam:SetAttribute('alpha', alpha)
				edgeBeam.Color = ColorSequence.new(Color3.new(1,1,1):Lerp(Color3.new(), 1-alpha))
			end

			edgeBeam.Attachment0 = att0
			edgeBeam.Attachment1 = att1
			edgeBeam.Parent = att0

			edgeAdornments[ key1 ] = edgeBeam
			
			--[[if i2%5 == 0 then
				task.wait()
			end]]
		end
	end
	
	return nodeAdornments, edgeAdornments
end

return Module
