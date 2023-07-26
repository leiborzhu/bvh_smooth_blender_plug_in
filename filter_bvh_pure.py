bl_info = {
    "name": "bvh smooth",
    "author": "leibor",
    "version": (1, 0),
    "blender": (3, 4, 0),
    "location": "View3D > Tools > bvh平滑处理",
    "description": "bvh关键帧顺滑",
    "warning": "",
    "doc_url": "",
    "category": "Object",
}

import bpy
import os

def deal_bvh(self, context, myProperty):
    # dir_path = r'D:\\light-project\\blenderIK\\test'
    
    # output_path = r'D:\light-project\blenderIK\output_bvh'

    print(myProperty.input_path)
    dir_path = myProperty.input_path.strip()
    output_path = myProperty.output_path.strip()
    smooth_time = myProperty.repeat_time
    # print(dir(myProperty))
    # base frame rate
    bpy.context.scene.render.fps_base = 1

    drop_file = []
    
    for i, file in enumerate(os.listdir(dir_path)):
        if not myProperty.cover and file in os.listdir(output_path):
            continue

        if '.bvh' in file:
            try:
                with open(os.path.join(dir_path, file)) as f:
                    lines = f.readlines()
                    for line in lines:
                        if 'Frames:' in line:
                            last_frame = int(line.strip('Frames:'))
                        
                        if 'Frame Time: ' in line:
                            frame_rate = int(round(1/float(line.strip('Frame Time: '))))
                            break
                bpy.context.scene.render.fps = frame_rate

                bpy.ops.import_anim.bvh(filepath=os.path.join(dir_path, file), rotate_mode='ZXY', axis_forward='Y', axis_up='Z')
                bpy.ops.object.posemode_toggle()
                bpy.ops.pose.select_all(action='SELECT')
                bpy.context.area.ui_type = 'FCURVES'
                bpy.context.scene.frame_current = 2 # timeline change

                bpy.ops.graph.select_leftright(mode='RIGHT', extend=False)
                for _ in range(smooth_time):
                    bpy.ops.graph.smooth()

                # output bvh
                bpy.ops.export_anim.bvh(filepath=os.path.join(output_path, file),
                                        check_existing=True,
                                        filter_glob='*.bvh',
                                        global_scale=1.0,
                                        frame_start=1,
                                        frame_end=last_frame,
                                        rotate_mode='ZXY', 
                                        root_transform_only=True)
                                            
                bpy.ops.object.posemode_toggle()
                bpy.ops.object.delete(use_global=False, confirm=False)

                # 清空所有骨架
                for arm in bpy.data.armatures:
                    bpy.data.armatures.remove(arm)
    
                # 清空所有动作
                for action in bpy.data.actions:
                    bpy.data.actions.remove(action)
            except:
                drop_file.append(file + '\n')
        print(i/len(os.listdir(dir_path)))
    else:
        drop_file.append(file + '\n')
    bpy.context.area.ui_type = 'VIEW_3D'

    with open(os.path.join(dir_path, 'drop_log.txt'), 'w') as f:
        f.writelines(drop_file)

# RNA属性
class myProperty(bpy.types.PropertyGroup):
    input_path: bpy.props.StringProperty(name='input_path')
    output_path: bpy.props.StringProperty(name='output_path')
    repeat_time: bpy.props.IntProperty(name='repeat_time',min=0) 
    cover: bpy.props.BoolProperty(name='cover') 

class bvhTools(bpy.types.Operator):
    # import bvh
    bl_label='bvh关键帧顺滑'
    bl_idname = 'obj.bvhsmooth' # no da xie
    bl_options = {"REGISTER", "UNDO"}
    
    mStr: bpy.props.StringProperty(name="mString", default="blender")
    
    def execute(self, context):
        myProperty = context.scene.myProperty
        deal_bvh(self, context, myProperty)
        return {'FINISHED'}

    
    
class PT_view3d(bpy.types.Panel):
    bl_idname = "PT_view3d"
    bl_label = "bvh平滑处理"

    # 标签分类
    bl_category = "Tool"

    # ui_type
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_context = "objectmode"

    def draw(self, context):
        layout = self.layout
        layout.label(text="批量处理", icon="BLENDER")
        row = layout.row()
        col = layout.column()
        scene = context.scene.myProperty

        col.prop(scene, 'input_path', text="bvh文件路径")
        col.prop(scene, 'output_path', text="输出路径")
        col.prop(scene, 'repeat_time', text="平滑次数")
        col.prop(scene, 'cover', text="是否覆盖")

        # 生成按钮
        row.operator("obj.bvhsmooth", text="导入",icon="CUBE").mStr = '开始'

class bvhSmooth(bpy.types.Header):
    
    bl_space_type = 'INFO'
    
    def draw(self, context):
        self.layout.operator('bl_idname')


    
classGroup = [myProperty,
            bvhTools,
            bvhSmooth,
            PT_view3d
]

def register():
    
    for item in classGroup:
        # print(1)
        bpy.utils.register_class(item)
    bpy.types.Scene.myProperty = bpy.props.PointerProperty(type=myProperty)
def unregister():
    for item in classGroup:
        bpy.utils.unregister_class(item)


if __name__== '__main__':
    register()
    
    