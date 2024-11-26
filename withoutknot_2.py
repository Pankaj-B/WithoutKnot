bl_info = {
    "name": "Without Knot 2.0",
    "author": "Pankaj_B.",
    "version": (1, 0),
    "blender": (4, 0, 0),
    "location": "View3D > Tool",
    "description": ("It works on 2D Bezier Curve/Spline"
                    "3 Different Variations"
                    "Create New Point Between 2 Points, Merge 2 Points, Append Next Spline"),
    "warning": "Its tested on Max 100 Bezier Points",
    "wiki_url": "https://github.com/Pankaj-B/WithoutKnot/wiki/Without-Knot-2.0",
    "category": "Tool",
}
import bpy
import math
def dtc1(pnt1, pnt2):
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(pnt1, pnt2)))
class OBJECT_OT_WithoutKnot(bpy.types.Operator):
    bl_idname = "object.without_knot"
    bl_label = "Without Knot"
    def execute(self, context):
        mt = context.scene.m_t
        if (mt.ckb_1 == False and mt.ckb_2== False and mt.ckb_3== False) or (mt.ckb_1 == True and mt.ckb_2== True and mt.ckb_3== True):
            self.report({'ERROR'}, "Select any option.")
            return {'CANCELLED'}
        obj = context.active_object
        if obj and obj.type == 'CURVE' and obj.data.splines:
            if obj.data.splines[0].type == 'BEZIER':
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.object.mode_set(mode='OBJECT')
                bpy.ops.object.mode_set(mode='EDIT')
                if obj.data.use_path:
                    obj.data.use_path = False
                slt_pt = []
                for sl_in, spline in enumerate(obj.data.splines):
                    for pt_in, point in enumerate(spline.bezier_points):
                        if point.select_control_point:
                            slt_pt.append((sl_in, point))
                if len(slt_pt) < 2:
                    self.report({'ERROR'}, "Select at least 2 points that belong to separate splines.")
                    return {'CANCELLED'}
                sp_idc = {sl_in for sl_in, _ in slt_pt}
                if len(sp_idc) < 2:
                    self.report({'ERROR'}, "Selected points must belong to separate splines.")
                    return {'CANCELLED'}
                for sl_in in sp_idc:
                    spline = obj.data.splines[sl_in]
                    if spline.use_cyclic_u:
                        self.report({'ERROR'}, "All splines of selected points must have cyclic_u set to False.")
                        return {'CANCELLED'}     
                slt_pt1 = []
                for sl_in, spline in enumerate(obj.data.splines):
                    for pt_in, point in enumerate(spline.bezier_points):
                        if point.select_control_point:
                            for point in spline.bezier_points:
                                if point.select_control_point:
                                    point.select_left_handle = True
                                    point.select_right_handle = True
                            slt_pt1.append({
                                'SlIn': sl_in,
                                'PtIn': pt_in,
                                'PtLc': point.co,
                                'RtHL': point.handle_right,
                                'LtHL': point.handle_left,
                                'RtHT': point.handle_right_type,
                                'LtHT': point.handle_left_type,
                            })                
                bpy.ops.curve.select_all(action='DESELECT')
                ft_sl_in = min(sp_idc)
                ft_sp = obj.data.splines[ft_sl_in]
                ftd = []                
                for pt_in, point in enumerate(ft_sp.bezier_points):
                    ftd.append({
                        'SlIn': ft_sl_in,
                        'PtIn': pt_in,
                        'PtLc': point.co,
                        'RtHL': point.handle_right,
                        'LtHL': point.handle_left,
                        'RtHT': point.handle_right_type,
                        'LtHT': point.handle_left_type,
                    })
                tpd = []
                ft_pt = ftd[0]['PtLc']
                lt_pt = ftd[-1]['PtLc']
                for sp_dt in slt_pt1:
                    if sp_dt['SlIn'] != ft_sl_in:
                        nt_sp = obj.data.splines[sp_dt['SlIn']]
                        ft_pt_nt_sp = nt_sp.bezier_points[0].co
                        if dtc1(ft_pt, ft_pt_nt_sp) < dtc1(lt_pt, ft_pt_nt_sp):
                            bpy.ops.curve.select_all(action='DESELECT')
                            for point in ft_sp.bezier_points:
                                point.select_control_point = True
                                point.select_left_handle = True
                                point.select_right_handle = True
                            bpy.ops.curve.switch_direction()
                            ftd = []
                            for pt_in, point in enumerate(ft_sp.bezier_points):
                                ftd.append({
                                    'SlIn': ft_sl_in,
                                    'PtIn': pt_in,
                                    'PtLc': point.co,
                                    'RtHL': point.handle_right,
                                    'LtHL': point.handle_left,
                                    'RtHT': point.handle_right_type,
                                    'LtHT': point.handle_left_type,
                                })
                            break
                tpd.extend(ftd)
                rem_sp = [d for d in slt_pt1 if d['SlIn'] != ft_sl_in]
                while rem_sp:
                    lt_pt = tpd[-1]['PtLc']
                    nt_sp = None
                    mn_dt = float('inf')
                    for data in rem_sp:
                        sl_in = data['SlIn']
                        spline = obj.data.splines[sl_in]
                        ft_pt = spline.bezier_points[0].co
                        lt_pt_sp = spline.bezier_points[-1].co
                        dt_ft = sum((a - b) ** 2 for a, b in zip(lt_pt[:2], ft_pt[:2])) ** 0.5
                        dt_lt = sum((a - b) ** 2 for a, b in zip(lt_pt[:2], lt_pt_sp[:2])) ** 0.5
                        if dt_lt < mn_dt:
                            mn_dt = dt_lt
                            nt_sp = sl_in
                            switch_direction = True
                        if dt_ft < mn_dt:
                            mn_dt = dt_ft
                            nt_sp = sl_in
                            switch_direction = False
                    if nt_sp is None:
                        break
                    if switch_direction:
                        bpy.ops.curve.select_all(action='DESELECT')
                        for point in obj.data.splines[nt_sp].bezier_points:
                            point.select_control_point = True
                            point.select_left_handle = True
                            point.select_right_handle = True
                        bpy.ops.curve.switch_direction()
                    nt_sp_dt = []
                    for pt_in, point in enumerate(obj.data.splines[nt_sp].bezier_points):
                        nt_sp_dt.append({
                            'SlIn': nt_sp,
                            'PtIn': pt_in,
                            'PtLc': point.co,
                            'RtHL': point.handle_right,
                            'LtHL': point.handle_left,
                            'RtHT': point.handle_right_type,
                            'LtHT': point.handle_left_type,
                        })
                    tpd.extend(nt_sp_dt)
                    rem_sp = [d for d in rem_sp if d['SlIn'] != nt_sp]
                    lt_pt = tpd[-1]['PtLc']
                ntpd = []                
                if(mt.ckb_1 == True or mt.ckb_2 == True):
                    i = 1
                    while i < len(tpd) - 1:
                        ct_sl_in = tpd[i]['SlIn']
                        while i < len(tpd) and tpd[i]['SlIn'] == ct_sl_in:
                            if i == len(tpd) - 1 or tpd[i + 1]['SlIn'] != ct_sl_in:
                                break
                            ntpd.append(tpd[i])
                            i += 1
                        if i < len(tpd) - 1:
                            if(mt.ckb_1 == True):
                                up_pt = {
                                    'SlIn': tpd[i]['SlIn'],
                                    'PtIn': tpd[i]['PtIn'],
                                    'PtLc': (tuple((a) for a, b in zip(tpd[i]['PtLc'], tpd[i + 1]['PtLc']))),
                                    'RtHL': tpd[i]['RtHL'],
                                    'LtHL': tpd[i]['LtHL'],
                                    'RtHT': 'FREE',
                                    'LtHT': 'FREE',
                                }
                                ntpd.append(up_pt)
                                up_pt = {
                                    'SlIn': tpd[i]['SlIn'],
                                    'PtIn': tpd[i]['PtIn'],
                                    'PtLc': (tuple((a + b) / 2 for a, b in zip(tpd[i]['PtLc'], tpd[i + 1]['PtLc']))),
                                    'RtHL': (tuple((b) for a, b in zip(tpd[i+1]['LtHL'], tpd[i + 1]['LtHL']))),
                                    'LtHL': (tuple((a) for a, b in zip(tpd[i]['RtHL'], tpd[i + 1]['RtHL']))),
                                    'RtHT': 'FREE',
                                    'LtHT': 'FREE',
                                }
                                ntpd.append(up_pt)
                                up_pt = {
                                    'SlIn': tpd[i]['SlIn'],
                                    'PtIn': tpd[i]['PtIn'],
                                    'PtLc': (tuple((b) for a, b in zip(tpd[i]['PtLc'], tpd[i + 1]['PtLc']))),
                                    'RtHL': tpd[i+1]['RtHL'],
                                    'LtHL': tpd[i+1]['LtHL'],
                                    'RtHT': 'FREE',
                                    'LtHT': 'FREE',
                                }
                                ntpd.append(up_pt)
                                i += 2
                            if(mt.ckb_2 == True):
                                up_pt = {
                                    'SlIn': tpd[i]['SlIn'],
                                    'PtIn': tpd[i]['PtIn'],
                                    'PtLc': (tuple((a + b) / 2 for a, b in zip(tpd[i]['PtLc'], tpd[i + 1]['PtLc']))),
                                    'RtHL': tpd[i+1]['RtHL'],
                                    'LtHL': tpd[i]['LtHL'],
                                    'RtHT': 'FREE',
                                    'LtHT': 'FREE',
                                }
                                ntpd.append(up_pt)
                                i += 2
                    if len(tpd) > 1:
                        if(mt.ckb_1 == True):
                            up_pt = {
                                'SlIn': tpd[-1]['SlIn'],
                                'PtIn': tpd[-1]['PtIn'],
                                'PtLc': (tuple((b) for a, b in zip(tpd[0]['PtLc'], tpd[-1]['PtLc']))),
                                'RtHL': (tuple((b) for a, b in zip(tpd[0]['RtHL'], tpd[-1]['RtHL']))),
                                'LtHL': (tuple((b) for a, b in zip(tpd[0]['LtHL'], tpd[-1]['LtHL']))),
                                'RtHT': 'FREE',
                                'LtHT': 'FREE',
                            }
                            ntpd.append(up_pt)
                            up_pt = {
                                'SlIn': tpd[-1]['SlIn'],
                                'PtIn': tpd[-1]['PtIn'],
                                'PtLc': (tuple((a + b) / 2 for a, b in zip(tpd[0]['PtLc'], tpd[-1]['PtLc']))),
                                'RtHL': (tuple((a) for a, b in zip(tpd[0]['LtHL'], tpd[-1]['RtHL']))),
                                'LtHL': (tuple((b) for a, b in zip(tpd[0]['LtHL'], tpd[-1]['RtHL']))),
                                'RtHT': 'FREE',
                                'LtHT': 'FREE',
                            }
                            ntpd.append(up_pt)
                            up_pt = {
                                'SlIn': tpd[-1]['SlIn'],
                                'PtIn': tpd[-1]['PtIn'],
                                'PtLc': (tuple((a) for a, b in zip(tpd[0]['PtLc'], tpd[-1]['PtLc']))),
                                'RtHL': (tuple((a) for a, b in zip(tpd[0]['RtHL'], tpd[-1]['RtHL']))),
                                'LtHL': (tuple((a) for a, b in zip(tpd[0]['LtHL'], tpd[-1]['LtHL']))),
                                'RtHT': 'FREE',
                                'LtHT': 'FREE',
                            }
                            ntpd.append(up_pt)
                        if(mt.ckb_2 == True):
                            up_pt = {
                                'SlIn': tpd[-1]['SlIn'],
                                'PtIn': tpd[-1]['PtIn'],
                                'PtLc': (tuple((a + b) / 2 for a, b in zip(tpd[0]['PtLc'], tpd[-1]['PtLc']))),
                                'RtHL': (tuple((a) for a, b in zip(tpd[0]['RtHL'], tpd[-1]['RtHL']))),
                                'LtHL': (tuple((b) for a, b in zip(tpd[0]['LtHL'], tpd[-1]['LtHL']))),
                                'RtHT': 'FREE',
                                'LtHT': 'FREE',
                            }
                            ntpd.append(up_pt)
                    tpd.clear()
                    tpd.extend(ntpd)
                    ntpd.clear()
                for sl_in in sp_idc:
                    spline = obj.data.splines[sl_in]
                    for point in spline.bezier_points:
                        point.select_control_point = True
                        point.select_left_handle = True
                        point.select_right_handle = True
                bpy.ops.curve.select_all(action='DESELECT')
                new_spline = obj.data.splines.new('BEZIER')
                new_spline.bezier_points.add(len(tpd) - 1)
                for i, data in enumerate(tpd):
                    point = new_spline.bezier_points[i]
                    point.co = data['PtLc']
                    point.handle_right = data['RtHL']
                    point.handle_left = data['LtHL']
                    point.handle_right_type = data['RtHT']
                    point.handle_left_type = data['LtHT']
                    point.select_control_point = True
                    point.select_left_handle = True
                    point.select_right_handle = True
                new_spline.use_cyclic_u = True 
                tpd.clear()
                ftd.clear()
                slt_pt.clear()
                sp_idc.clear()
            else:
                self.report({'WARNING'}, "Active object is not a Bezier curve")
        else:
            self.report({'WARNING'}, "No active object or not a curve")
        return {'FINISHED'}
class OptCho(bpy.types.PropertyGroup):
    ckb_1: bpy.props.BoolProperty(name="Bridge")
    ckb_2: bpy.props.BoolProperty(name="Merge")
    ckb_3: bpy.props.BoolProperty(name="Append")
class OBJECT_PT_DisKnot(bpy.types.Panel):
    bl_label = "Without Knot 2.0"
    bl_idname = "OBJECT_PT_dis_knot"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Tool'
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        mt = scene.m_t
        layout.prop(mt, "ckb_1")
        layout.prop(mt, "ckb_2")
        layout.prop(mt, "ckb_3")    
        layout.operator("object.without_knot")
def register():
    bpy.utils.register_class(OBJECT_OT_WithoutKnot)
    bpy.utils.register_class(OBJECT_PT_DisKnot)
    bpy.utils.register_class(OptCho)
    bpy.types.Scene.m_t = bpy.props.PointerProperty(type=OptCho)
def unregister():
    bpy.utils.unregister_class(OBJECT_PT_DisKnot)
    bpy.utils.unregister_class(OBJECT_OT_WithoutKnot)
    bpy.utils.unregister_class(OptCho)
    del bpy.types.Scene.m_t
if __name__ == "__main__":
    register()
