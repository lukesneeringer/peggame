class Board:
    """A peg board is represented to a human as an equilateral
    triangle with 15 spaces."""
    
    def __init__(self, initial_holes, ancestor=None):
        """Initialize the board.
        
        I will represent the peg locations as two-tuples representing
        coordinates. Although the Cracker Barrel game uses a visually
        equilateral triangle, we may use a right triangle for our data
        representation as long as we translate possible moves correctly;
        a peg can now move horizontal, vertical, or move BOTH the x and y
        coordinate in the same direction (but not opposite directions).
        
        Therefore, my data representation looks like this:
        
        (0,0)
        (1,0) (1,1)
        (2,0) (2,1) (2,2)
        (3,0) (3,1) (3,2) (3,3)
        (4,0) (4,1) (4,2) (4,3) (4,4)
        
        Note that, for my purposes, the y-axis is inverted (0 at the top,
        4 at the bottom)."""
        
        # initialize the set of pegs
        self.pegs = []
        
        # the initial_holes argument may be a single tuple (one hole),
        # or a tuple of tuples (many holes). Make the argument into a
        # tuple of tuples regardless.
        if type(initial_holes[0]) != tuple:
            initial_holes = (initial_holes,)
        
        # place pegs on the pegboard, leaving holes in the tuple
        # indicated by the initial_holes argument
        for i in range(0, 5):
            for j in range(0, i + 1):
                if (i, j) not in initial_holes:
                    self.pegs.append(Peg(self, (i, j)))
                    
        # boards should be aware of their ancestor boards, if any
        self._ancestor = ancestor
                
    def __contains__(self, arg):
        """Return True if the given position on the board, represented
        by a position tuple, contains a peg, False otherwise.
        If a Peg is given, return True if the Peg is part of the board
        and still exists on the board."""
        
        # sanity check: was a Peg provided? if so, check self.pegs
        if type(arg) == Peg:
            return arg in self.pegs
            
        # sanity check: was I given a valid position tuple?
        if type(arg) != tuple or len(arg) != 2:
            raise ValueError
        if arg[0] > 4 or arg[1] > arg[0]:
            return False
            
        # okay, is that position filled in the current pegboard?
        for peg in self.pegs:
            if peg.x == arg[0] and peg.y == arg[1]:
                return True
        return False
        
    def __len__(self):
        """Return the number of pegs on the pegboard."""
        return len(self.pegs)
                
    def __unicode__(self):
        """Return a string representation of the board."""
        
        s = ''
        for i in range(0, 5):
            s += (' ' * (4 - i))
            for j in range(0, i + 1):
                if (i, j) in self:
                    s += '* '
                else:
                    s += '- '
            s += '\n'
        return s
        
    def __str__(self):
        return self.__unicode__()
    
    @property    
    def valid_moves(self):
        """Return a list of all valid moves available to every peg on
        the board."""
        
        # have I computed this already?
        if hasattr(self, '_moves'):
            return self._moves
        
        # retrieve a list of valid moves
        self._moves = []
        for peg in self.pegs:
            self._moves += peg.valid_moves
            
        return self._moves
          
    def move(self, from_, to):
        """Return a new board that is identical to this board, except
        with the peg in position "from" moved to the position "to", and the
        in-between peg removed."""
        
        # create a list of positions without pegs on the new board
        positions_without_pegs = []
        
        # iterate over the positions...
        for i in range(0, 5):
            for j in range(0, i + 1):
                # first, is there not a peg there now? there still won't be,
                # as long as I'm not moving my new peg to there...
                if (i, j) not in self and (i, j) != to:
                    positions_without_pegs.append((i, j))
                    
                # is this the position being vacated?
                if (i, j) == from_:
                    positions_without_pegs.append((i, j))
                    
                # is this the position being hopped and therefore
                # having its peg removed from the board?
                if (to[0] - from_[0]) / 2 == to[0] - i and (to[1] - from_[1]) / 2 == to[1] - j:
                    positions_without_pegs.append((i, j))
                    
        # create and return a **new** board with this board as its ancestor
        return Board(positions_without_pegs, ancestor=self)
        
    @property
    def ancestry(self):
        """Return a list of the entire ancestry of this baord."""
        
        # iterate over all of the ancestors until I get to the original board
        # and return them in a list, beginning with the original (oldest) board
        answer = [self]
        while answer[0]._ancestor is not None:
            answer.insert(0, answer[0]._ancestor)
        return answer
        
    @property
    def solution(self):
        """Based on this pegboard, return an accurate solution pegboard."""
        
        # has a solution already been cached?
        if hasattr(self, '_solution'):
            return self._solution
        
        # sanity check: is this board itself a solution?
        if len(self) == 1:
            return self
            
        # get a list of all possible new boards from here; if any of
        # those boards are a valid solution, just stop and return
        # that board
        for m in self.valid_moves:
            new_board = self.move(*m)
            if new_board.solution is not None:
                self._solution = new_board.solution
                return self._solution
                
        # all new boards have been exhausted recursively;
        # there is no solution here
        self._solution = None
        return self._solution
            
class Peg:
    """A peg on the pegboard."""
    
    def __init__(self, board, position):
        # assign values
        self.board = board
        self.x = position[0]
        self.y = position[1]
        
        # sanity check: is the position given a valid pegboard position?
        if self.x > 4 or self.y > self.x:
            raise ValueError
            
    def __eq__(self, other):
        if self.board == other.board and self.position == other.position:
            return True
        return False
        
    @property
    def position(self):
        """Return this peg's position as a tuple."""
        return (self.x, self.y)

    @property
    def valid_moves(self):
        """Return a list of all valid moves for this peg. A move is represented as a
        tuple of two tuples (from, to).
        If this peg has no valid moves, return an empty list."""
        
        # have I already computed this?
        if hasattr(self, '_valid_moves'):
            return self._valid_moves
        
        # any peg can make six possible moves, which can be thought of as deltas from
        # the peg's current position: (-2, -2), (-2, 0), (0, -2), (0, 2), (2, 0), (2, 2)
        self._valid_moves = []
        for x in range(-2, 4, 2):
            for y in range(-2, 4, 2):
                # sanity check: (-2, 2), (2, -2), and (0, 0) aren't valid moves,
                # but they'll be included in my iterators above
                if x * -1 == y:
                    continue
                    
                # does the space this peg wants to move to actually exist?
                if self.x + x not in range(0, 5) or self.y + y not in range(0, 5) or self.y + y > self.x + x:
                    continue
                    
                # ...and is the space free?
                if (self.x + x, self.y + y) in self.board:
                    continue
                
                # is there a peg to be hopped at the intermediary space?
                if (self.x + (x / 2), self.y + (y / 2)) not in self.board:
                    continue
                    
                # okay, this position is a valid move
                self._valid_moves.append(((self.x, self.y), (self.x + x, self.y + y)))
                
        return self._valid_moves
        
# okay, now compute the actual solution: there are only six meaningful starting points (the top six
# in the triangle); all others have symmetrical equivalents depending on how you turn the triangle
boards = []
for i in range(0, 3):
    for j in range(0, i + 1):
        boards.append(Board((i, j)))
        
# iterate over each of my six starting boards and hunt down a solution; once one is found, print
# that solution out and stop
for board in boards:
    if board.solution is not None:
        for b in board.solution.ancestry:
            print b
    break