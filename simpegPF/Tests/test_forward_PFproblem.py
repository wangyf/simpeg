import unittest
from SimPEG import *
import matplotlib.pyplot as plt
import simpegPF as PF


class MagFwdProblemTests(unittest.TestCase):

    def setUp(self):

        hxind = ((5,25,1.3),(41, 12.5),(5,25,1.3))
        hyind = ((5,25,1.3),(41, 12.5),(5,25,1.3))
        hzind = ((5,25,1.3),(40, 12.5),(5,25,1.3))
        hx, hy, hz = Utils.meshTensors(hxind, hyind, hzind)
        M = Mesh.TensorMesh([hx, hy, hz], [-hx.sum()/2,-hy.sum()/2,-hz.sum()/2])

        chibkg = 0.
        chiblk = 0.01
        chi = np.ones(M.nC)*chibkg
        sph_ind = PF.MagAnalytics.spheremodel(M, 0., 0., 0., 100)
        chi[sph_ind] = chiblk
        model = PF.BaseMag.BaseMagModel(M)
        prob = PF.Magnetics.MagneticsDiffSecondary(M, model)
        self.prob = prob
        self.M = M
        self.chi = chi


    def test_anal_forward(self):

        data = PF.BaseMag.BaseMagData()

        Inc = 90.
        Dec = 0.
        Btot = 51000

        b0 = PF.MagAnalytics.IDTtoxyz(Inc, Dec, Btot)        
        data.setBackgroundField(Inc, Dec, Btot)
        xr = np.linspace(-300, 300, 41)
        yr = np.linspace(-300, 300, 41)
        X, Y = np.meshgrid(xr, yr)
        Z = np.ones((xr.size, yr.size))*150
        rxLoc = np.c_[Utils.mkvc(X), Utils.mkvc(Y), Utils.mkvc(Z)]
        data.rxLoc = rxLoc
            
        self.prob.pair(data)
        u = self.prob.fields(self.chi)
        B = u['B']

        bxa,bya,bza = PF.MagAnalytics.MagSphereAnalFunA(rxLoc[:,0],rxLoc[:,1],rxLoc[:,2],100.,0.,0.,0.,0.01, b0,'secondary') 
       
        dpred = data.projectFieldsAsVector(B)
        err = np.linalg.norm(dpred-np.r_[bxa, bya, bza])/np.linalg.norm(np.r_[bxa, bya, bza])

        if err > 0.05:
            raise Exception('Anaytic test is failed T.T')
        else:
            print "Anaytic test is passed"
            pass
    
if __name__ == '__main__':
    unittest.main()
