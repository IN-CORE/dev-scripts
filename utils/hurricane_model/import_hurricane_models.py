import hdf5storage as hd
import numpy as np
import json
import scipy.io as spio
import json_minify as jsonm

def parse_file(name: str):
    try:
        path_loc = "/Users/vnarah2/incore-data/Hurricane wind field/mat-to-json/Models/"
        # Models' mat files can be found on box: https://uofi.box.com/s/tc366nux02oeoc71y3hbpgs42ok0m2kw
        path = path_loc+"Model_" + name + ".mat"
        data = hd.loadmat(path)
        #matdata = spio.loadmat(path)
        jason = {}
        times_arr = np.array(data["absTime"]).tolist()
        jason["times"] = times_arr
        times = len(times_arr)
        jason["Rs"] = convert_Rs(np.array(data["Rs"]).transpose(0,2,1), times)
        jason["VTs_o"] = ilist_to_strlist(np.array(data["VTs_o"]).flatten().tolist())
        jason["VTs_o_new"] = ilist_to_strlist(np.array(data["VTs_o_new"]).flatten().tolist())

        jason["center_lati_o"] = np.array(data["center_lati_o"]).flatten().tolist()
        jason["center_long_o"] = np.array(data["center_long_o"]).flatten().tolist()
        jason["center_lati_o_new"] = np.array(data["center_lati_o_new"]).flatten().tolist()
        jason["center_long_o_new"] = np.array(data["center_long_o_new"]).flatten().tolist()

        jason["contouraxis_zones_fitted"] = convert_ndarrList(np.array(data["contouraxis_zones_fitted"]).flatten().tolist())

        jason["crossP"] = data["crossP"].tolist()[0]

        jason["index_hwind_time_radii"] = np.array(data["index_hwind_time_radii"]).flatten().tolist()

        jason["index_landfall"] = data["index_landfall"].tolist()[0][0]

        jason["miss_info_fitted"] = convert_ndarrList(np.array(data["miss_info_fitted"]).flatten().tolist())

        jason["nofiles"] = data["nofiles"].tolist()[0]

        jason["omega_miss_fitted"] = convert_ndList(np.array(data["omega_miss_fitted"]).flatten().tolist())

        para = np.array(data["para"]).flatten().tolist()

        arrPara = []
        i = 0
        for p in para:
            #while (i < 3):
            arrPara.append(format_para(p, 'all'))
             #   i = i+1


        jason["para"] = arrPara
        jason["time_radii"] = np.array(data["time_radii"]).flatten().tolist()
        jason["time_radii_new"] = np.array(data["time_radii_new"]).flatten().tolist()

        with open(path_loc+name+'.json', 'w') as outfile:
            json.dump(jason, outfile, separators=(',',':'))

        #print(json.dumps(jason))

    except IOError:
        return "Cant read/load mat file"


def format_para(para:list, type='all'):
    b_outer = para[0]["B_outer"][0][0][0]
    b_inner = para[0]["B_inner"][0][0][0]
    f = para[0]["f"][0][0][0]
    rm_outer = para[0]["Rm_outer"][0][0][0]
    rm_inner = para[0]["Rm_inner"][0][0][0]
    fr = para[0]["Fr"][0][0][0]
    pc = para[0]["pc"][0][0][0]
    contouraxis_outer = para[0]["contouraxis_outer"][0].tolist()[0]
    contouraxis_inner = para[0]["contouraxis_inner"][0].tolist()[0]

    rm_theta_vsp_outer_arr = para[0]["Rm_theta_Vsp_outer"][0]
    rm_theta_vsp_outer = [ilist_to_strlist(rm_theta_vsp_outer_arr[i].flatten().tolist()) for i in range(0, len(rm_theta_vsp_outer_arr))]

    rm_theta_vsp_inner_arr = para[0]["Rm_theta_Vsp_inner"][0]
    rm_theta_vsp_inner = [rm_theta_vsp_inner_arr[i].flatten().tolist() for i in range(0, len(rm_theta_vsp_inner_arr))]
    rm_theta_vsp_inner = round_subLists(rm_theta_vsp_inner)

    vg_outer_arr = para[0]["Vg_outer"][0]
    vg_outer = [vg_outer_arr[i].flatten().tolist() for i in range(0, len(vg_outer_arr))]
    #vg_outer = round_subLists(vg_outer)

    vg_inner_arr = para[0]["Vg_inner"][0]
    vg_inner = [vg_inner_arr[i].flatten().tolist() for i in range(0, len(vg_inner_arr))]
    #vg_inner = round_subLists(vg_inner)

    j ={}

    if type == 'outer':
       return {'rm_theta_vsp_outer': rm_theta_vsp_outer}
    elif type == 'inner':
        return {'rm_theta_vsp_inner': rm_theta_vsp_inner}
    elif type == 'none':
        return {}

    return {
        'b_outer': b_outer, 'b_inner': b_inner, 'f': f, 'pc':float(pc),
        'rm_outer': float(rm_outer), 'rm_inner': float(rm_inner), 'fr': fr,
        'rm_theta_vsp_outer': rm_theta_vsp_outer,
        'rm_theta_vsp_inner': rm_theta_vsp_inner,
        'contouraxis_outer': contouraxis_outer,
        'contouraxis_inner': contouraxis_inner,
        'vg_outer': vg_outer, 'vg_inner': vg_inner,
    }

def convert_ndarrList_rec(l:list):
    arr = []
    for x in l:
        if not isinstance(x, np.ndarray):
            convert_ndarrList(x)
        else:
            arr.append(x.flatten().tolist())
    return arr

def convert_ndarrList(l:list):
    arr = []
    for x in l:
        arr.append(x.tolist())

    return arr


def convert_ndList(l: list):
    arr=[]
    for x in range(0,len(l)):
        row = []
        for y in range(0, len(l[x])):
            elem = []
            for z in range(0,len(l[x][y])):
                elem.append(l[x][y][z].flatten().tolist())

            flat_list = [item for sublist in elem for item in sublist]
            row.append(flat_list)

        arr.append(row)
    return arr

def convert_Rs(arr, times):
    final = []
    for x in range(0,times):
        final.append([
            {"mexico": arr[0][x].tolist()},
            {"usa": arr[1][x].tolist()},
            {"jam": arr[2][x].tolist()},
            {"cuba": arr[3][x].tolist()}
        ])
    return final

def ilist_to_strlist(iList):
    strList = []
    for x in iList:
        #x = complex(x)
        if isinstance(x, complex):
            y = complex(round(x.real, 3), round(x.imag, 3) if x.imag != 0 else x.imag)
        else:
            y=round(x,3)

        strList.append(str(y).strip('()')) # Also replace braces?
    return strList

def round_subLists(l:list):
    n = []
    for i in range(0, len(l)):
        r =[]
        for j in range(0, len(l[i])):
            if isinstance(l[i][j], complex):
                y = complex(round(l[i][j].real, 3),
                    round(l[i][j].imag, 3) if l[i][j].imag != 0 else l[i][j].imag)
                y= str(y).strip('()')
            else:
                y = round(l[i][j], 3)

            r.append(y)
        n.append(r)
    return n

if __name__ == '__main__':
    name = "Katrina2"
    #path = "/Users/vnarah2/incore-data/Hurricane wind field/mat-to-json/Models/Model_"+name+".mat"
    parse_file(name)
