# from https://github.com/elkebir-group/UniPPM/blob/master/CNF.py
# thanks!

class CNF:

    def __init__(self, first_fresh_var):
        self.ind=[]
        self.var = first_fresh_var
        self.true_var = first_fresh_var
        self.clauses=[[self.true_var]]

#basic functions
    def true(self):
        return self.true_var
    
    def false(self):
        return -self.true_var
    
    def new_var(self,ind=False):
        self.var+=1
        if(ind): self.ind.append(self.var)
        return self.var
    
    def AND(self,a,b,r=None):
        if (r==None): r=self.new_var()
        self.clauses.append([r,-a,-b])
        self.clauses.append([-r,a])
        self.clauses.append([-r,b])
        return r

    def OR(self,a,b,r=None):
        if (r==None): r=self.new_var()
        self.clauses.append([-r,a,b])
        self.clauses.append([r,-a])
        self.clauses.append([r,-b])
        return r

    def XOR(self,a,b,r=None):
        if (r==None): r=self.new_var()
        self.clauses.append([-r,a,b])
        self.clauses.append([-r,-a,-b])
        self.clauses.append([r,a,-b])
        self.clauses.append([r,-a,b])
        return r
    
    def only_one_in_all(self,literals):
        self.clauses.append(literals)
        for i in range(len(literals)):
            for j in range(i):
                self.clauses.append([-literals[i],-literals[j]])

    def set_true(self,lit):
        self.clauses.append([lit])


#calcultions
    def half_adder(self,a,b,result,carry):
        self.XOR(a,b,result)
        self.AND(a,b,carry)
    
    def full_adder(self,a,b,c,result,carry):
        r1=self.new_var()
        c1=self.new_var()
        self.half_adder(a,b,r1,c1)
        c2=self.new_var()
        self.half_adder(r1,c,result,c2)
        self.OR(c1,c2,carry)
    
    def add(self,a,b,r=None):
        #clauses.append(["c","add"])
        Len=len(a)
        if r==None:
            r=[ self.new_var() for i in range(Len)]
        c = [self.new_var() for i in range(Len)]
        for i in range(Len):
            if i==0 :
                self.half_adder(a[i],b[i],r[i],c[i])
            else:
                self.full_adder(a[i],b[i],c[i-1],r[i],c[i])
        self.clauses.append([-c[-1]])
        #clauses.append(["c","end_add"])
        return r
    
    def leq(self,a,b,opt=0):#~a+b+1
        Len=len(a)
        comp_a=[-l for l in a]
        r= [ self.new_var() for i in range(Len)]
        c =[ self.new_var() for i in range(Len)]
        for i in range(Len):
            if i==0 :
                self.full_adder(comp_a[i],b[i],1,r[i],c[i])
            else:
                self.full_adder(comp_a[i],b[i],c[i-1],r[i],c[i])
        if(opt==0):self.clauses.append([c[-1]])
        return c[-1]
    
    def eq(self,a,b):
        Len=len(a)
        for i in range(Len):
            self.clauses.append([-a[i],b[i]])
            self.clauses.append([a[i],-b[i]])
        return
    
    def max_(self,a,b,r=None):
        Len=len(a)
        if r==None:
            r = [ self.new_var() for i in range(Len)]
        alb=self.leq(a,b,opt=1)
        for i in range(Len):
            self.OR( self.AND(-alb, a[i]), self.AND(alb, b[i]) , r[i] )
        return r
    
    def increment(self,a,b=1,r=None):
        Len=len(a)
        if r==None:
            r=[ self.new_var() for i in range(Len)]
        c = [self.new_var() for i in range(Len)]
        for i in range(Len):
            if i==0 :
                self.half_adder(a[i],b,r[i],c[i])
            else:
                self.half_adder(a[i],c[i-1],r[i],c[i])
        #clauses.append([-c[-1]])
        return r
    
    def add_clause(self,lits):
        self.clauses.append(lits)
        
    def ORList(self,lits,r=None):
        if r==None:
            r=self.new_var()
        self.clauses.append([-r]+lits)
        for lit in lits:
            self.clauses.append([r, -lit])
        return r

#save_file
    def to_cnf_file(self,filename,show_additional_comments=False):
        fcnf=open(filename,"w")
        
        fcnf.write("p cnf %d %d\n"%(self.var,len(self.clauses)))

        for i,ind_var in enumerate(self.ind):
            if i%10 == 0: fcnf.write("c ind ")
            fcnf.write ("%d "%ind_var)
            if i%10 == 9 or i==len(self.ind)-1: fcnf.write("0\n")
        
        for cl in self.clauses:
            if cl[0]=="c":
                if show_additional_comments:
                    fcnf.write("c %s\n"%cl[1])
                continue
            for lit in cl:
                fcnf.write("%d "%lit)
            fcnf.write("0\n")
        
        fcnf.close()