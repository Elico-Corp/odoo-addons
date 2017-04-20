# -*- coding: utf8 -*-
from openerp.osv import fields, osv
from datetime import datetime, timedelta
import time
from openerp.tools.translate import _

## Project task
#
#  
class project_task(osv.osv):
    _inherit="project.task"
    _order = "date_start" 
    
    _columns={    
             }
    
    ## Surcharge of create method
    #  @param self The object pointer. 
    #  @param cr The database connection(cursor)
    #  @param uid The id of user performing the operation
    #  @param vals The dictionary of field values to update 
    #  @param context The optional dictionary of contextual parameters such as user language
    #       
    def create(self, cr, uid, vals, context=None):
        return super(project_task, self).create(cr, uid, vals, context=context)

    ## Surcharge of write method  
    #  @param self The object pointer. 
    #  @param cr The database connection(cursor)
    #  @param uid The id of user performing the operation
    #  @param vals The dictionary of field values to update
    #  @param context The optional dictionary of contextual parameters such as user language
    #       
    def write(self, cr, uid, ids, vals, context=None): 
        return super(project_task,self).write(cr, uid, ids, vals, context=context)
    
project_task()

## Crm meeting
#
#  
class crm_meeting(osv.osv):
    _inherit="crm.meeting"
    _order = "date"
    
    _columns={  
              }
    
crm_meeting()

## Crm helpdesk 
#
#  
class crm_helpdesk(osv.osv):
    _inherit="crm.helpdesk"
    _order = "date"
    
    _columns={   
             }
    
crm_helpdesk()

## This class contains information and method of the capacity planning
#
#  
class capacity_planning(osv.osv):
    _name = "capacity.planning"
    _description = "Capacity Planning" 
    _order = "startdate"
     
    ## Method to retrieve the list of ids of tasks to configure the planning   
    #  @param self The object pointer. 
    #  @param cr The database connection(cursor)
    #  @param uid The id of user performing the operation
    #  @param ids The list of record ids or single integer when there is only one id
    #  @param vals The dictionary of field values to update
    #  @param context The optional dictionary of contextual parameters such as user language
    #   
    def _get_id_task_capacity_planning(self, cr, uid, ids, field_name, arg, context):
        res = {}
        task_obj = self.pool.get('project.task')
        idss = task_obj.search(cr,uid,[('state','!=',['done','cancelled']),('user_id','=',uid)])
        idss_select = task_obj.browse(cr,uid,idss)
        for i in ids:
            res.setdefault(i, [])
            idplann = i
        for m in idss_select:
            if not m.user_id or not m.date_deadline or not m.date_start:
                res[idplann].append(m.id)    
        return res
 
    ## Method to retrieve the list of ids of meetings to configure the planning   
    #  @param self The object pointer. 
    #  @param cr The database connection(cursor)
    #  @param uid The id of user performing the operation
    #  @param ids The list of record ids or single integer when there is only one id
    #  @param vals The dictionary of field values to update
    #  @param context The optional dictionary of contextual parameters such as user language
    #  
    def _get_id_meeting_capacity_planning(self, cr, uid, ids, field_name, arg, context):
        res = {}
        idss=self.pool.get('crm.meeting').search(cr,uid,['|',('user_id','=',None),('state','=','draft'),('user_id','=',uid)])
        for i in ids:
            res.setdefault(i, [])
            idplann = i
        for m in idss:
            res[idplann].append(m)
        return res

    ## Method to retrieve the list of ids of helpdesks to configure the planning   
    #  @param self The object pointer. 
    #  @param cr The database connection(cursor)
    #  @param uid The id of user performing the operation
    #  @param ids The list of record ids or single integer when there is only one id
    #  @param vals The dictionary of field values to update
    #  @param context The optional dictionary of contextual parameters such as user language
    #  
    def _get_id_helpdesk_capacity_planning(self, cr, uid, ids, field_name, arg, context):
        res = {}
        idss=self.pool.get('crm.helpdesk').search(cr,uid,['|',('user_id','=',None),('state','=','draft'),('user_id','=',uid)])
        for i in ids:
            res.setdefault(i, [])
            idplann = i
        for m in idss:
            res[idplann].append(m)
        return res
    
    _columns = {   
        'name':fields.char('Name',size=64, required=True,help="The name of your planning."),
        'startdate': fields.date('Start Date', required=True,help="The start date of your planning."),
        'enddate': fields.date('End Date',required=True,help="The end date of your planning."),
        'tpstotal':fields.float('Total time',help="The number of hours available for selected resources in the planning period."),
        'tpsoccup':fields.float('Busy time',help="The number of hours already used."),
        'tpsdispo':fields.float('Time available',help="The number of hours available for work."),
        'busy':fields.float('Busy %',digits=(5,2),group_operator="avg"),
        'id':fields.integer('ID'),
        'planning_user':fields.one2many('capacity.planning.user', 'planning_id', 'Planning By Employee'),
        'sel_department':fields.many2one('hr.department','Department',help="Only if you want just one department for the capacity planning."),
        'planning_before':fields.one2many('capacity.planning.before', 'planning_id', 'Before the planning'),
        'planning_without_deadline':fields.one2many('capacity.planning.without.deadline', 'planning_id', 'Without deadline'),
        'task':fields.function(_get_id_task_capacity_planning,method=True,string="Project Name", type='many2many',relation='project.task'),
        'meeting':fields.function(_get_id_meeting_capacity_planning,method=True,string="Project Name", type='many2many',relation='crm.meeting'),
        'helpdesk':fields.function(_get_id_helpdesk_capacity_planning,method=True,string="Project Name", type='many2many',relation='crm.helpdesk'),
    }

    _defaults = {
        'startdate': lambda *a: time.strftime('%Y-%m-%d'),
        'enddate': lambda *a: time.strftime('%Y-%m-%d'),
    }

    ## Surcharge of write method
    #  @param self The object pointer. 
    #  @param cr The database connection(cursor)
    #  @param uid The id of user performing the operation
    #  @param ids The list of record ids or single integer when there is only one id
    #  @param vals The dictionary of field values to update
    #  @param context The optional dictionary of contextual parameters such as user language
    #       
    def write(self, cr, uid, ids, vals, context=None):                
        return super(capacity_planning,self).write(cr, uid, ids, vals, context=context)
    
    ## Surcharge of create method for add employee
    #  @param self The object pointer. 
    #  @param cr The database connection(cursor)
    #  @param uid The id of user performing the operation
    #  @param vals The dictionary of field values to update
    #  @param context The optional dictionary of contextual parameters such as user language
    #   
    def create(self, cr, uid, vals, context=None):
        #check if the end date is less than the start date
        if vals['enddate'] < vals['startdate']:
            raise osv.except_osv('Error !','End date < Start date.')      
        #create the schedule and store its ID
        new_planning_id = super(capacity_planning,self).create(cr, uid, vals, context=context)
        #store information about current capacity planning
        plan_obj = self.pool.get('capacity.planning')
        plan_ids = plan_obj.search(cr,uid,[('id','=',new_planning_id)])
        plan_rec = plan_obj.browse(cr,uid,plan_ids)
        #add all employes or just a department
        addall = True
        #number of department
        numdepart = 0
        for pl in plan_rec:
            if pl.sel_department.name != None:
                addall = False
                numdepart = pl.sel_department.id
        #fetch all employee or department        
        emp_obj = self.pool.get('hr.employee')
        if addall:
            emp_ids = emp_obj.search(cr,uid,[('active','=',True),('id','!=',1)])
        else:
            emp_ids = emp_obj.search(cr,uid,[('active','=',True),('department_id','=',numdepart),('id','!=',1)])    
        emp_rec = emp_obj.browse(cr,uid,emp_ids)
        #add employee with working schedule or not
        create = False
        for emp in emp_rec:
            id_w=0
            if emp.contract_id.date_start<pl.enddate:
                id_w=emp.contract_id.working_hours
            self.pool.get('capacity.planning.user').create(cr, uid, {'emp':emp.resource_id.name,'iduser': emp.resource_id.user_id,'idresource':emp.resource_id.id,'idemp':emp.id,'departement': emp.department_id.name, 'planning_id': new_planning_id,'idhourofwork':id_w}, context=context)
            self.pool.get('capacity.planning.before').create(cr, uid, {'emp':emp.resource_id.name,'iduser': emp.resource_id.user_id,'idresource':emp.resource_id.id,'idemp':emp.id,'departement': emp.department_id.name, 'planning_id': new_planning_id,'idhourofwork':id_w}, context=context)
            self.pool.get('capacity.planning.without.deadline').create(cr, uid, {'emp':emp.resource_id.name,'iduser': emp.resource_id.user_id,'idresource':emp.resource_id.id,'idemp':emp.id,'departement': emp.department_id.name, 'planning_id': new_planning_id,'idhourofwork':id_w}, context=context)
        return new_planning_id
    
    ## Method for update information 
    #  @param self The object pointer. 
    #  @param cr The database connection(cursor)
    #  @param uid The id of user performing the operation
    #  @param ids The list of record ids or single integer when there is only one id
    #  @param context The optional dictionary of contextual parameters such as user language
    #  
    def check_update_capacity(self, cr, uid ,ids, context=None):
        objplan = self.browse(cr, uid, ids[0], context=context)
        #current planning
        idplan = objplan.id
        plan_obj = self.pool.get('capacity.planning')
        plan_ids = plan_obj.search(cr,uid,[('id','=',idplan)])
        plan_rec = plan_obj.browse(cr,uid,plan_ids)
        #department of employee
        numdepart = 0
        if plan_rec[0].sel_department.name != None:
            numdepart = plan_rec[0].sel_department.id
        startdatecapacityplanning = plan_rec[0].startdate
        enddatecapacityplanning = plan_rec[0].enddate                   
        #fetch employee
        emp_obj = self.pool.get('hr.employee')
        if numdepart == 0:
            emp_ids = emp_obj.search(cr,uid,[('resource_id','!=',None),('id','!=',1)])
        else:
            emp_ids = emp_obj.search(cr,uid,[('department_id','=',numdepart),('id','!=',1)])    
        emp_rec = emp_obj.browse(cr,uid,emp_ids) 
        create = False
        emp_plan_obj = self.pool.get('capacity.planning.user')
        emp_plan_ids = emp_plan_obj.search(cr,uid,[('planning_id','=',idplan)])
        emp_plan_rec = emp_plan_obj.browse(cr,uid,emp_plan_ids)
        before_obj = self.pool.get('capacity.planning.before')
        before_ids = before_obj.search(cr,uid,[('planning_id','=',idplan)])
        before_rec = before_obj.browse(cr,uid,before_ids)
        deadline_obj = self.pool.get('capacity.planning.without.deadline')
        deadline_ids = deadline_obj.search(cr,uid,[('planning_id','=',idplan)])
        deadline_rec = deadline_obj.browse(cr,uid,deadline_ids)
        #loop for update list of employee 
        for emp in emp_rec:                  
            create = False
            for emp_plan in emp_plan_rec:             
                if emp_plan.idresource == emp.resource_id.id:
                    create = False
                    break
                else:
                    create = True 
            #create with contract  
            if create:
                #fetch contract or not      
                id_w=0
                if emp.contract_id.working_hours:
                    id_w=emp.contract_id.working_hours
                self.pool.get('capacity.planning.user').create(cr, uid, {'emp':emp.resource_id.name,'iduser': emp.resource_id.user_id,'idresource':emp.resource_id.id,'idemp':emp.id,'departement': emp.department_id.name, 'planning_id': idplan,'idhourofwork':id_w}, context=context)
                self.pool.get('capacity.planning.before').create(cr, uid, {'emp':emp.resource_id.name,'iduser': emp.resource_id.user_id,'idresource':emp.resource_id.id,'idemp':emp.id,'departement': emp.department_id.name, 'planning_id': idplan,'idhourofwork':id_w}, context=context)
                self.pool.get('capacity.planning.without.deadline').create(cr, uid, {'emp':emp.resource_id.name,'iduser': emp.resource_id.user_id,'idresource':emp.resource_id.id,'idemp':emp.id,'departement': emp.department_id.name, 'planning_id': idplan,'idhourofwork':id_w}, context=context)
        #loop for update list of employee 
        for emp_plan in emp_plan_rec:
            testremove = False
            for emp in emp_rec:
                if emp_plan.idresource == emp.resource_id.id:
                    testremove = True
                else:
                    if testremove != True:
                        testremove = False                                        
            if not testremove:
                emp_plan_obj.unlink(cr,uid,emp_plan.id)
                before_obj.unlink(cr,uid,emp_plan.id)
                deadline_obj.unlink(cr,uid,emp_plan.id)
        #fetch employee
        emp_plan_obj = self.pool.get('capacity.planning.user')
        emp_plan_ids = emp_plan_obj.search(cr,uid,[('planning_id','=',idplan)])
        emp_plan_rec = emp_plan_obj.browse(cr,uid,emp_plan_ids)        
        #meeting
        meeting_obj = self.pool.get('crm.meeting')
        meeting_ids = meeting_obj.search(cr,uid,[('state','in',('open','draft')),('end_date','=',None)])
        meeting_rec = meeting_obj.browse(cr,uid,meeting_ids)        
        #task
        task_obj = self.pool.get('project.task')
        task_ids = task_obj.search(cr,uid,[('state','in',('open','draft','done'))])
        task_rec = task_obj.browse(cr,uid,task_ids)        
        #leave
        holi_obj = self.pool.get('hr.holidays')
        holi_ids = holi_obj.search(cr,uid,[('type','=','remove'),('date_to','!=',None),('date_from','!=',None),('state','=','validate')])
        holi_rec = holi_obj.browse(cr,uid,holi_ids)       
        #helpdesk 
        hd_obj = self.pool.get('crm.helpdesk')
        hd_ids = hd_obj.search(cr,uid,[('state','in',('open','draft'))])
        hd_rec = hd_obj.browse(cr,uid,hd_ids)       
        #for capacity planning
        busytotal = tpstotal = availabletotal = 0
        #loop on employee  
        for emp_plan in emp_plan_rec:
            e_obj = self.pool.get('hr.employee')
            e_ids = e_obj.search(cr,uid,[('id','=',emp_plan.idemp)])
            e_rec = e_obj.browse(cr,uid,e_ids)
            #number of meeting
            #total time of meeting   
            #number of task   
            #total time of task
            #number of leave
            #total time of leave
            #fetch time of task
            #total busy time for each employee
            #number of meeting before capacity planning
            #number of task before capacity planning
            #number of tasks not started or without start date
            #number of leave before capacity planning
            #number of tasks without end date
            #number of heldesk for each employee
            #number of helpdesk before capacity planning
            #period of planning for each contract 
            nbmeeting=hmeeting=nbtask=htask=nbholiday=hholiday=meetingtime=busy=nbmeetbefore=nbtaskbefore=nbtasknotstarted=nbholidaybefore=nbwithoutdeadline=nbhelpdesk=nbhelpdeskbefore=0
            datecontratstart=datecontratstop=datecontrat=datecontno=False
            startdatecapacityplanning = plan_rec[0].startdate
            enddatecapacityplanning = plan_rec[0].enddate                  
            if e_rec[0].contract_id.date_end != False:
                #begins and ends within                      
                if e_rec[0].contract_id.date_end < enddatecapacityplanning: 
                    if e_rec[0].contract_id.date_end > startdatecapacityplanning: 
                        if e_rec[0].contract_id.date_start > startdatecapacityplanning:
                            datecontrat = True
                            startdatecapacityplanning = e_rec[0].contract_id.date_start 
                            enddatecapacityplanning = e_rec[0].contract_id.date_end                              
                        #begins before and ends within
                        else:
                            datecontratstop = True
                            enddatecapacityplanning = e_rec[0].contract_id.date_end                
                if e_rec[0].contract_id.date_start < startdatecapacityplanning:
                    if e_rec[0].contract_id.date_end > enddatecapacityplanning:
                        datecontno = False                                       
                #starts in and ends after
                if e_rec[0].contract_id.date_start < enddatecapacityplanning:
                    if e_rec[0].contract_id.date_start > startdatecapacityplanning:
                        if (e_rec[0].contract_id.date_end > enddatecapacityplanning):
                            datecontratstart = True
                            startdatecapacityplanning = e_rec[0].contract_id.date_start
                #begins after
                if(e_rec[0].contract_id.date_start > enddatecapacityplanning):
                    datecontno = True              
                if(e_rec[0].contract_id.date_end < startdatecapacityplanning):
                    datecontno = True           
            else:
                #begins within
                if e_rec[0].contract_id.date_start < enddatecapacityplanning and e_rec[0].contract_id.date_start > startdatecapacityplanning:
                    datecontratstart = True
                    startdatecapacityplanning = e_rec[0].contract_id.date_start 
                #begins before
                if e_rec[0].contract_id.date_start < startdatecapacityplanning:
                    datecontratstart = True
                    datecontno = False
                    #startdatecapacityplanning = cont.date_start                                              
                #begins after
                if(e_rec[0].contract_id.date_start > enddatecapacityplanning):
                    datecontno = True  
            if datecontno:
                self.pool.get('capacity.planning.user').write(cr, uid, emp_plan.id, {'idhourofwork':0,'busyp':100.0,'iduser': e_rec[0].resource_id.user_id})
            else:
                self.pool.get('capacity.planning.user').write(cr, uid, emp_plan.id, {'idhourofwork':e_rec[0].contract_id.working_hours,'iduser': e_rec[0].resource_id.user_id})                                        
            #if the employee has a working schedule
            if emp_plan.idhourofwork != 0 and e_rec[0].contract_id.date_start < enddatecapacityplanning:                
                for meet in meeting_rec:                   
                    if emp_plan.iduser == meet.user_id.id:                       
                        #if the meeting starts and finished in the planning                  
                        if (startdatecapacityplanning <= meet.date) and (enddatecapacityplanning >= meet.date_deadline):
                            nbmeeting += 1
                            meetingtime = self.generate_tpstotal(cr,uid,emp_plan.id,2, meet.date, meet.date_deadline,context=None)                      
                            #if the generating time is greater than the length of the meeting time keep the meeting and the total addition time Meetings
                            if (meet.duration < meetingtime) and (meetingtime > 0):
                                hmeeting += meet.duration
                            else:   
                                hmeeting += meetingtime                                             
                        #if the meeting starts in the planning and ends after
                        if (meet.date >= startdatecapacityplanning) and (meet.date < enddatecapacityplanning) and (meet.date_deadline > enddatecapacityplanning):                
                            #number of days the planning in
                            datein1 = datetime.strptime(meet.date,"%Y-%m-%d %H:%M:%S")             
                            datein2 = datetime.strptime(enddatecapacityplanning,"%Y-%m-%d")
                            datein = datein2 -datein1
                            timein = int(datein.days)                         
                            #number of days the planning out
                            dateout1 = datetime.strptime(enddatecapacityplanning,"%Y-%m-%d")
                            dateout2 = datetime.strptime(meet.date_deadline,"%Y-%m-%d %H:%M:%S")
                            dateout = dateout2 - dateout1
                            timeout = int(dateout.days)                    
                            #total number of days of the meeting
                            timeinout = timein + timeout                       
                            #calculating the percentage being on the inside
                            ptimeinout = float(timeinout) / 1 
                            ptimein = float(timein) / ptimeinout      
                            nbmeeting += 1
                            meetingtime = self.generate_tpstotal(cr,uid,emp_plan.id,2, meet.date, meet.date_deadline,context=None)
                            #calculating and adding the percentage being in the planning
                            if meet.duration < meetingtime:
                                hmeeting += meet.duration * ptimein
                            else:   
                                hmeeting += meetingtime * ptimein                            
                        #if the meeting start before and end inside
                        if (startdatecapacityplanning > meet.date) and (startdatecapacityplanning < meet.date_deadline) and (enddatecapacityplanning >= meet.date_deadline):
                            datein1 = datetime.strptime(startdatecapacityplanning,"%Y-%m-%d")
                            datein2 = datetime.strptime(meet.date_deadline,"%Y-%m-%d %H:%M:%S")
                            datein = datein2 - datein1
                            timein = int(datein.days)
                            dateout1 = datetime.strptime(startdatecapacityplanning,"%Y-%m-%d")
                            dateout2 = datetime.strptime(meet.date,"%Y-%m-%d %H:%M:%S")
                            dateout = dateout1 - dateout2
                            timeout = int(dateout.days)
                            timeinout = timein + timeout 
                            ptimeinout = float(timeinout) / 1 
                            ptimein = float(timein) / ptimeinout
                            nbmeeting += 1
                            meetingtime = self.generate_tpstotal(cr,uid,emp_plan.id,2, meet.date, meet.date_deadline,context=None)
                            if meet.duration < meetingtime:
                                hmeeting += meet.duration * ptimein
                            else:   
                                hmeeting += meetingtime * ptimein                        
                        #if the meeting start before and end after    
                        if (startdatecapacityplanning > meet.date) and (enddatecapacityplanning < meet.date_deadline):
                            datein1 = datetime.strptime(startdatecapacityplanning,"%Y-%m-%d")
                            datein2 = datetime.strptime(enddatecapacityplanning,"%Y-%m-%d")
                            datein = datein2 - datein1
                            timein = int(datein.days)
                            dateout1 = datetime.strptime(startdatecapacityplanning,"%Y-%m-%d")
                            dateout2 = datetime.strptime(meet.date,"%Y-%m-%d %H:%M:%S")   
                            dateout = dateout1 - dateout2
                            timeout1 = int(dateout.days) 
                            dateout1 = datetime.strptime(enddatecapacityplanning,"%Y-%m-%d")                           
                            dateout2 = datetime.strptime(meet.date_deadline,"%Y-%m-%d %H:%M:%S")                            
                            dateout = dateout2 - dateout1                           
                            timeout2 = int(dateout.days) 
                            timeout = timeout1 + timeout2                            
                            timeinout = timein + timeout  
                            ptimeinout = float(timeinout) / 1 
                            ptimein = float(timein) / ptimeinout
                            nbmeeting += 1
                            meetingtime = self.generate_tpstotal(cr,uid,emp_plan.id,2, meet.date, meet.date_deadline,context=None)
                            if meet.duration < meetingtime:
                                hmeeting += meet.duration * ptimein
                            else:   
                                hmeeting += meetingtime * ptimein                       
                        #if the meeting end before
                        if (startdatecapacityplanning > meet.date_deadline):
                            nbmeetbefore += 1                          
                #task                           
                for ta in task_rec:  
                    if emp_plan.iduser == ta.user_id.id:  
                        if ta.state != 'done':                      
                            if ta.date_deadline:                            
                                if ta.date_start:
                                    if (startdatecapacityplanning <= ta.date_start) and (enddatecapacityplanning >= ta.date_deadline):
                                        nbtask += 1
                                        if ta.remaining_hours > 0:
                                            htask += ta.remaining_hours                                
                                    if (startdatecapacityplanning <= ta.date_start) and (enddatecapacityplanning > ta.date_start) and (enddatecapacityplanning < ta.date_deadline):   
                                        datein1 = datetime.strptime(ta.date_start,"%Y-%m-%d %H:%M:%S")
                                        datein2 = datetime.strptime(enddatecapacityplanning,"%Y-%m-%d")
                                        datein = datein2 - datein1
                                        timein = int(datein.days)
                                        dateout1 = datetime.strptime(enddatecapacityplanning,"%Y-%m-%d")
                                        dateout2 = datetime.strptime(ta.date_deadline,"%Y-%m-%d")
                                        dateout = dateout2 - dateout1
                                        timeout = int(dateout.days)
                                        timeinout = timein + timeout  
                                        ptimeinout = float(timeinout) / 1 
                                        ptimein = float(timein) / ptimeinout
                                        nbtask += 1
                                        if ta.remaining_hours > 0:
                                            htask += ta.remaining_hours * ptimein                              
                                    if (startdatecapacityplanning > ta.date_start) and (startdatecapacityplanning < ta.date_deadline) and (enddatecapacityplanning >= ta.date_deadline): 
                                        nbtask += 1
                                        if ta.remaining_hours > 0:
                                            htask += ta.remaining_hours                             
                                    if (startdatecapacityplanning > ta.date_start) and (enddatecapacityplanning < ta.date_deadline):
                                        datein1 = datetime.strptime(startdatecapacityplanning,"%Y-%m-%d")
                                        datein2 = datetime.strptime(enddatecapacityplanning,"%Y-%m-%d")
                                        datein = datein2 - datein1
                                        timein = int(datein.days)
                                        dateout1 = datetime.strptime(startdatecapacityplanning,"%Y-%m-%d")
                                        dateout2 = datetime.strptime(ta.date_start,"%Y-%m-%d %H:%M:%S")   
                                        dateout = dateout1 - dateout2
                                        timeout1 = int(dateout.days) 
                                        dateout1 = datetime.strptime(enddatecapacityplanning,"%Y-%m-%d")                           
                                        dateout2 = datetime.strptime(ta.date_deadline,"%Y-%m-%d")                            
                                        dateout = dateout2 - dateout1                           
                                        timeout2 = int(dateout.days) 
                                        timeout = timeout1 + timeout2                            
                                        timeinout = timein + timeout  
                                        ptimeinout = float(timeinout) / 1 
                                        ptimein = float(timein) / ptimeinout
                                        nbtask += 1
                                        if ta.remaining_hours > 0:
                                            htask += ta.remaining_hours * ptimein                             
                                    if (startdatecapacityplanning > ta.date_deadline):
                                        nbtaskbefore += 1                                    
                                else:
                                    nbtasknotstarted += 1                            
                            else:
                                nbwithoutdeadline += 1  
                    if ta.state=='done':
                        if (ta.date_start < enddatecapacityplanning) and (ta.date_deadline > startdatecapacityplanning):
                            for p in ta.work_ids:
                                if emp_plan.iduser == p.user_id.id: 
                                    if (p.date >= startdatecapacityplanning) and (p.date < enddatecapacityplanning):
                                        htask+=p.hours
                                        nbtask += 1
                #leave
                for ho in holi_rec:
                    holidaytime = 0                   
                    if emp_plan.iduser == ho.user_id.id:
                        if (startdatecapacityplanning <= ho.date_from) and (enddatecapacityplanning >= ho.date_to):
                            holidaytime = self.generate_tpstotal(cr,uid,emp_plan.id,3,ho.date_from,ho.date_to,context=None)
                            hholiday += holidaytime 
                            nbholiday += 1                 
                        if (startdatecapacityplanning > ho.date_from) and (startdatecapacityplanning < ho.date_to) and (enddatecapacityplanning >= ho.date_to):
                            date = datetime.strptime(startdatecapacityplanning,"%Y-%m-%d")
                            st = date.strftime("%Y-%m-%d %H:%M:%S")
                            holidaytime = self.generate_tpstotal(cr,uid,emp_plan.id,3,st,ho.date_to,context=None)
                            hholiday += holidaytime 
                            nbholiday += 1                    
                        if (startdatecapacityplanning <= ho.date_from) and (enddatecapacityplanning > ho.date_from) and (enddatecapacityplanning < ho.date_to):
                            date = datetime.strptime(enddatecapacityplanning,"%Y-%m-%d")
                            enddate = date.strftime("%Y-%m-%d %H:%M:%S")
                            holidaytime = self.generate_tpstotal(cr,uid,emp_plan.id,3,ho.date_from,enddate,context=None)
                            hholiday += holidaytime   
                            nbholiday += 1                      
                        if (startdatecapacityplanning > ho.date_from) and (enddatecapacityplanning < ho.date_to):
                            date = datetime.strptime(startdatecapacityplanning,"%Y-%m-%d")
                            startdate = date.strftime("%Y-%m-%d %H:%M:%S")
                            date = datetime.strptime(enddatecapacityplanning,"%Y-%m-%d")                            
                            enddate = date.strftime("%Y-%m-%d %H:%M:%S")
                            holidaytime = self.generate_tpstotal(cr,uid,emp_plan.id,3,startdate,enddate,context=None)
                            hholiday += holidaytime
                            nbholiday += 1                   
                        if (startdatecapacityplanning > ho.date_to):
                            nbholidaybefore += 1            
                #helpdesk    
                for helpdesk in hd_rec:
                    if emp_plan.iduser == helpdesk.user_id.id: 
                        if (startdatecapacityplanning <= helpdesk.date) and (enddatecapacityplanning >= helpdesk.date):
                            nbhelpdesk += 1  
                        if (startdatecapacityplanning > helpdesk.date):
                            nbhelpdeskbefore += 1                                  
            #calculation of the total occupation time of the employee
            busy = hmeeting + htask + hholiday
            #calculating the total time of the planning
            busytotal += busy 
            id_w=0
            if e_rec[0].contract_id.date_start < enddatecapacityplanning: 
                id_w=e_rec[0].contract_id.working_hours
            self.pool.get('capacity.planning.user').write(cr, uid, emp_plan.id, {'nbmeeting': nbmeeting, 'hmeeting': hmeeting,'nbtask':nbtask,'htask':htask, 'tpsoccupemp':busy, 'nbconge': nbholiday,'hconge':hholiday,'nbhelpdesk':nbhelpdesk,'idhourofwork':id_w})                  
            self.pool.get('capacity.planning.before').write(cr, uid, emp_plan.id, {'nbmeeting': nbmeetbefore,'nbtask':nbtaskbefore,'nbconge': nbholidaybefore,'nbhelpdesk':nbhelpdeskbefore,'idhourofwork':id_w})
            self.pool.get('capacity.planning.without.deadline').write(cr, uid, emp_plan.id, {'nbtask1':nbwithoutdeadline,'nbtask2':nbtasknotstarted,'idhourofwork':id_w})
            #calculation of the total time available for the planning period
            if datecontratstart:
                tpstotal += self.generate_tpstotal(cr, uid, emp_plan.id, 4, startdatecapacityplanning, None, context=None)
            elif datecontratstop:
                tpstotal += self.generate_tpstotal(cr, uid, emp_plan.id, 5, None, enddatecapacityplanning, context=None)
            elif datecontrat:
                tpstotal += self.generate_tpstotal(cr, uid, emp_plan.id, 6, startdatecapacityplanning, enddatecapacityplanning, context=None)
            elif datecontno:
                tpstotal += self.generate_tpstotal(cr, uid, emp_plan.id, 7, startdatecapacityplanning, enddatecapacityplanning, context=None)
            else:
                tpstotal += self.generate_tpstotal(cr,uid,emp_plan.id,1, None, None,context=None)    
        #calculation of the total time available for the planning period
        availabletotal = tpstotal - busytotal   
        #percentage available
        temp1 = tpstotal/100
        if availabletotal != 0:
            busy = busytotal / temp1
        else:
            busy = 0     
        self.pool.get('capacity.planning').write(cr,uid,idplan,{'tpstotal':tpstotal,'tpsoccup':busytotal,'tpsdispo':availabletotal,'busy':busy})   
        return True  
    
    ## Method for update capacity planning
    #  @param self The object pointer.    
    #  @param cr The database connection(cursor)
    #  @param uid The id of user performing the operation
    #  @param context The optional dictionary of contextual parameters such as user language
    #   
    def check_cron(self, cr, uid, context=None):
        capacity_obj = self.pool.get('capacity.planning')
        capacity_ids = capacity_obj.search(cr,uid,[])
        capacity_rec = capacity_obj.browse(cr,uid,capacity_ids)           
        for c in capacity_rec:
            temp=[]
            temp.append(c.id)
            self.check_update_capacity(cr, uid, temp, context=context)         
        return True
    
    ## Surcharge of the unlink method for delete resource when the capacity planning is delete
    #  @param self The object pointer. 
    #  @param cr The database connection(cursor)
    #  @param uid The id of user performing the operation
    #  @param ids The list of record ids or single integer when there is only one id
    #  @param delall Additional information
    #  
    def unlink(self, cr, uid, ids,delall = None, *args, **kwargs):
        objplan = self.browse(cr, uid, ids[0], context=None)
        idplan = objplan.id        
        emp_obj = self.pool.get('capacity.planning.user')
        emp_ids = emp_obj.search(cr,uid,[('planning_id','=',idplan)])
        emp_obj.unlink(cr,uid,emp_ids)
        emp_obj = self.pool.get('capacity.planning.before')
        emp_ids = emp_obj.search(cr,uid,[('planning_id','=',idplan)])
        emp_obj.unlink(cr,uid,emp_ids)
        emp_obj = self.pool.get('capacity.planning.without.deadline')
        emp_ids = emp_obj.search(cr,uid,[('planning_id','=',idplan)])
        emp_obj.unlink(cr,uid,emp_ids)
        return super(capacity_planning,self).unlink(cr, uid, ids,*args, **kwargs) 
    
    ## Method for calculate the total time between two dates
    #  @param self The object pointer. 
    #  @param cr The database connection(cursor)
    #  @param uid The id of user performing the operation
    #  @param ids The list of record ids or single integer when there is only one id
    #  @param select Number of case for the different solution
    #  @param sd The startdate
    #  @param ed The enddate
    #  @param context The optional dictionary of contextual parameters such as user language
    # 
    def generate_tpstotal(self, cr, uid, ids, select, sd, ed, context=None):
        htotal=nbmo=nbtu=nbwe=nbth=nbfr=nbsa=nbsu=i=0
        emp_obj = self.pool.get('capacity.planning.user').browse(cr, uid, ids, context=None)
        idplan = emp_obj.planning_id.id
        hbusy = emp_obj.tpsoccupemp
        plan_obj = self.pool.get('capacity.planning')
        plan_ids = plan_obj.search(cr,uid,[('id','=',idplan)])
        plan_rec = plan_obj.browse(cr,uid,plan_ids)
        for plan in plan_rec:
            #take the start date and end date of planning   
            if select == 1:       
                date = datetime.strptime(plan.startdate,"%Y-%m-%d")
                startdate = datetime.strptime(plan.startdate,"%Y-%m-%d")
                enddate = datetime.strptime(plan.enddate,"%Y-%m-%d")
            #data in argument
            if (select == 2) or (select == 3):
                date = datetime.strptime(sd,"%Y-%m-%d %H:%M:%S")
                startdate = datetime.strptime(sd,"%Y-%m-%d %H:%M:%S")
                enddate = datetime.strptime(ed,"%Y-%m-%d %H:%M:%S")
            #rule for different contracts
            if (select == 4):
                date = datetime.strptime(sd,"%Y-%m-%d")
                startdate = datetime.strptime(sd,"%Y-%m-%d")
                enddate = datetime.strptime(plan.enddate,"%Y-%m-%d")
            if (select == 5):
                date = datetime.strptime(plan.startdate,"%Y-%m-%d")
                startdate = datetime.strptime(plan.startdate,"%Y-%m-%d")
                enddate = datetime.strptime(ed,"%Y-%m-%d")
            if (select == 6):
                date = datetime.strptime(sd,"%Y-%m-%d")
                startdate = datetime.strptime(sd,"%Y-%m-%d")
                enddate = datetime.strptime(ed,"%Y-%m-%d")
            if (select == 7):
                date = datetime.strptime(ed,"%Y-%m-%d")
                startdate = datetime.strptime(ed,"%Y-%m-%d")
                enddate = datetime.strptime(ed,"%Y-%m-%d")          
            #starting day of the period 1 lundi dimanche 7
            numstartday = date.strftime("%u")
            diff = enddate - startdate
            nbjour = diff.days +1
            numday = int(numstartday) 
        #loop to have the number for each day
        while i!= nbjour:
            if numday == 1:
                nbmo +=1
            if numday == 2:
                nbtu +=1
            if numday == 3:
                nbwe +=1
            if numday == 4:
                nbth +=1
            if numday == 5:
                nbfr +=1
            if numday == 6:
                nbsa +=1
            if numday == 7:
                nbsu +=1
            numday += 1
            if numday == 8:
                numday = 0
            else:
                i += 1       
        #check if the day off is in the attendance and soustract this
        if emp_obj.idhourofwork != 0:
            j = 0
            day_off_obj = self.pool.get('training.holiday.period')
            if day_off_obj!=None:
                day_off_ids = day_off_obj.search(cr,uid,[])
                day_off_rec = day_off_obj.browse(cr,uid,day_off_ids)      
                for d in day_off_rec:
                    #start date of the period
                    date_s_temp = datetime.strptime(d.date_start,"%Y-%m-%d")
                    #end date of the period
                    date_e_temp = datetime.strptime(d.date_stop,"%Y-%m-%d")
                    date_s_temp_pl=datetime.strptime(plan_rec[0].startdate,"%Y-%m-%d")
                    date_e_temp_pl=datetime.strptime(plan_rec[0].enddate,"%Y-%m-%d")                 
                    #test if the period is in the planning
                    if (date_s_temp <= date_e_temp_pl) and (date_e_temp >= date_s_temp_pl): 
                        #ajust the start date and the and date on the planning
                        if date_s_temp <= date_s_temp_pl:
                            date_s=date_s_temp_pl
                            date_e=date_e_temp
                        elif date_e_temp >= date_e_temp_pl:
                            date_s=date_s_temp
                            date_e=date_e_temp_pl
                        else:
                            date_s=date_s_temp
                            date_e=date_e_temp                           
                        #start day of the week 
                        day_d = date_s.strftime("%u")
                        numday_d = int(day_d) 
                        #number of day for this period
                        diff_d = date_e - date_s
                        nbjour_d = diff_d.days+1                 
                        while j < nbjour_d:
                            if numday_d == 1:
                                nbmo -=1
                            if numday_d == 2:
                                nbtu -=1
                            if numday_d == 3:
                                nbwe -=1
                            if numday_d == 4:
                                nbth -=1
                            if numday_d == 5:
                                nbfr -=1
                            if numday_d == 6:
                                nbsa -=1
                            if numday_d == 7:
                                nbsu -=1
                            numday_d += 1
                            if numday_d == 8:
                                numday_d = 0
                            else:
                                j += 1                                                                             
        numhoraire = emp_obj.idhourofwork  
        if numhoraire != 0:
            hor_obj = self.pool.get('resource.calendar.attendance')
            hor_ids = hor_obj.search(cr,uid,[('calendar_id','=',numhoraire)])
            hor_rec = hor_obj.browse(cr,uid,hor_ids)        
            hmo=htu=hwe=hth=hfr=hsa=hsu=0     
            #added for each day the number of hours of working schedule
            for hor in hor_rec:
                if int(hor.dayofweek) == 0:
                    hmo += hor.hour_to - hor.hour_from
                if int(hor.dayofweek) == 1:
                    htu += hor.hour_to - hor.hour_from
                if int(hor.dayofweek) == 2:
                    hwe += hor.hour_to - hor.hour_from
                if int(hor.dayofweek) == 3:
                    hth += hor.hour_to - hor.hour_from
                if int(hor.dayofweek) == 4:
                    hfr += hor.hour_to - hor.hour_from
                if int(hor.dayofweek) == 5:
                    hsa += hor.hour_to - hor.hour_from
                if int(hor.dayofweek) == 6:
                    hsu += hor.hour_to - hor.hour_from       
            #multiplied by the number of days      
            hmo = hmo * nbmo
            htu = htu * nbtu
            hwe = hwe * nbwe
            hth = hth * nbth
            hfr = hfr * nbfr
            hsa = hsa * nbsa
            hsu = hsu * nbsu       
            #total time of the calculation period
            htotal = hmo + htu + hwe + hth + hfr + hsa + hsu
            #calculating the total time available
            hdispo = htotal - hbusy      
            #percentage
            if select != 3:
                hdispo = htotal - hbusy
                temp = htotal/100      
                if temp != 0:
                    pourcentage = hbusy/float(temp)
                else:
                    pourcentage = 100.0
                if (select == 7):
                    self.pool.get('capacity.planning.user').write(cr, uid, emp_obj.id, {'tpstotalemp': 0,'tpsdispoemp':0,'busyp':100.0,'idhourofwork':0})
                else:
                    self.pool.get('capacity.planning.user').write(cr, uid, emp_obj.id, {'tpstotalemp': htotal,'tpsdispoemp':hdispo,'busyp':pourcentage})
        return htotal     

capacity_planning()

## This class contains the employee for each capacity planning
#
#  
class capacity_planning_user(osv.osv):
    _name = "capacity.planning.user"
    _description = "Planning by Employee"
    _order = "emp" 
    
    _columns = {
        'planning_id': fields.many2one('capacity.planning', 'Planning'),
        'emp' : fields.char('Employe', size=30),
        'departement':fields.char('Department',size=30),
        'tpstotalemp':fields.float('Total time'),
        'tpsoccupemp':fields.float('Busy time'),
        'tpsdispoemp':fields.float('Available time'),
        'nbtask':fields.integer('Nb tasks'),
        'htask':fields.float('Tasks time'),
        'nbmeeting':fields.integer('Nb meeting'),
        'hmeeting':fields.float('Meeting time'),
        'nbconge':fields.integer('Nb leave'),
        'hconge':fields.float('Leave time'),
        'nbhelpdesk':fields.integer('Nb helpdesk'),
        'busyp':fields.float('Busy %',group_operator="avg"),
        'iduser':fields.integer('IDuser'),
        'idresource':fields.integer('IDresource'), 
        'idemp':fields.integer('IDemploye'),
        'idhourofwork':fields.integer('IDhourofwork'),   
    }
    
    ## Surcharge of the unlink method 
    #  @param self The object pointer. 
    #  @param cr The database connection(cursor)
    #  @param uid The id of user performing the operation
    #  @param ids The list of record ids or single integer when there is only one id
    #  
    def unlink(self, cr, uid, ids, *args, **kwargs):
        return super(capacity_planning_user,self).unlink(cr, uid, ids,*args, **kwargs) 
    
    ## Method for switch view in shared calendar
    #  @param self The object pointer. 
    #  @param cr The database connection(cursor)
    #  @param uid The id of user performing the operation
    #  @param ids The list of record ids or single integer when there is only one id
    #  @param context The optional dictionary of contextual parameters such as user language
    #  
    def check_shared_calendar(self, cr, uid, ids, context=None):      
        if context is None:
            context = {}
        obj = self.browse(cr, uid, ids[0], context=context)
        return {
            'name':'Shared calendar',
            'view_type': 'calendar,form,tree',
            'view_mode': 'calendar,form,tree',
            'domain': [('responsible', '=', obj.emp)],
            'res_model': 'shared.calendar',
            'target': 'new',
            'type': 'ir.actions.act_window',
        }  
        
    ## Method for switch view in the employee view
    #  @param self The object pointer. 
    #  @param cr The database connection(cursor)
    #  @param uid The id of user performing the operation
    #  @param ids The list of record ids or single integer when there is only one id
    #  @param context The optional dictionary of contextual parameters such as user language
    #         
    def check_employee(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        obj = self.browse(cr, uid, ids[0], context=context)
        return {
            'name':'Employee',
            'view_type': 'list,form,tree',
            'view_mode': 'list,form,tree',
            'domain': [('employee_id.id', '=', obj.idemp)],
            'res_model': 'hr.contract',
            'target': 'current',
            'type': 'ir.actions.act_window',
        }  
    
capacity_planning_user()

## This class contains the informations of objects before the planing
#
#  
class capacity_planning_before(osv.osv):
    _name = "capacity.planning.before"
    _description = "Before the planning"
    _order = "emp"
     
    _columns = {
        'planning_id': fields.many2one('capacity.planning', 'Planning'),
        'emp' : fields.char('Employe', size=30),
        'departement':fields.char('Department',size=30),
        'nbtask':fields.integer('Nb tasks'),
        'nbmeeting':fields.integer('Nb meeting'),
        'nbhelpdesk':fields.integer('Nb helpdesk'),
        'nbconge':fields.integer('Nb leave'),
        'iduser':fields.integer('IDuser'),
        'idresource':fields.integer('IDresource'), 
        'idemp':fields.integer('IDemploye'),
        'idhourofwork':fields.integer('IDhourofwork'),   
    }
    
    ## Method for switch view in task view
    #  @param self The object pointer. 
    #  @param cr The database connection(cursor)
    #  @param uid The id of user performing the operation
    #  @param ids The list of record ids or single integer when there is only one id
    #  @param context The optional dictionary of contextual parameters such as user language
    # 
    def check_task(self,cr,uid,ids,context=None):
        if context is None:
            context = {}
        obj = self.browse(cr, uid, ids[0], context=context)   
        obj2 = self.pool.get('capacity.planning')
        ids = obj2.search(cr,uid,[('id','=',obj.planning_id.id)])
        pl = obj2.browse(cr, uid, ids, context=context)
        for p in pl:
            start = p.startdate
        
        return {
            'name':'Tasks',
            'view_type': 'list',
            'view_mode': 'list',
            'res_model': 'project.task',
            'domain': [('user_id', '=', obj.iduser),('date_deadline','<',start)],
            'type': 'ir.actions.act_window',
            'target': 'new',
        } 
        
    ## Method for switch view in meeting view
    #  @param self The object pointer. 
    #  @param cr The database connection(cursor)
    #  @param uid The id of user performing the operation
    #  @param ids The list of record ids or single integer when there is only one id
    #  @param context The optional dictionary of contextual parameters such as user language
    # 
    def check_meeting(self,cr,uid,ids,context=None):
        if context is None:
            context = {}
        obj = self.browse(cr, uid, ids[0], context=context)        
        obj2 = self.pool.get('capacity.planning')
        ids = obj2.search(cr,uid,[('id','=',obj.planning_id.id)])
        pl = obj2.browse(cr, uid, ids, context=context)
        for p in pl:
            start = p.startdate
        
        return {
            'name':'Meetings',
            'view_type': 'list',
            'view_mode': 'list',
            'res_model': 'crm.meeting',
            'domain': [('user_id', '=', obj.iduser),('date_deadline','<',start)],
            'type': 'ir.actions.act_window',
            'target': 'new',
        } 
        
    ## Method for switch view in helpdesk view
    #  @param self The object pointer. 
    #  @param cr The database connection(cursor)
    #  @param uid The id of user performing the operation
    #  @param ids The list of record ids or single integer when there is only one id
    #  @param context The optional dictionary of contextual parameters such as user language
    # 
    def check_helpdesk(self,cr,uid,ids,context=None):        
        if context is None:
            context = {}
        obj = self.browse(cr, uid, ids[0], context=context)        
        obj2 = self.pool.get('capacity.planning')
        ids = obj2.search(cr,uid,[('id','=',obj.planning_id.id)])
        pl = obj2.browse(cr, uid, ids, context=context)
        for p in pl:
            start = p.startdate
        
        return {
            'name':'Helpdesks',
            'view_type': 'list',
            'view_mode': 'list',
            'res_model': 'crm.helpdesk',
            'domain': [('user_id', '=', obj.iduser),('date','<',start)],
            'type': 'ir.actions.act_window',
            'target': 'new',
        } 
        
    ## Method for switch view in leave view
    #  @param self The object pointer. 
    #  @param cr The database connection(cursor)
    #  @param uid The id of user performing the operation
    #  @param ids The list of record ids or single integer when there is only one id
    #  @param context The optional dictionary of contextual parameters such as user language
    # 
    def check_leave(self,cr,uid,ids,context=None):        
        if context is None:
            context = {}
        obj = self.browse(cr, uid, ids[0], context=context)         
        obj2 = self.pool.get('capacity.planning')
        ids = obj2.search(cr,uid,[('id','=',obj.planning_id.id)])
        pl = obj2.browse(cr, uid, ids, context=context)
        for p in pl:
            start = p.startdate
        
        return {
            'name':'Leaves',
            'view_type': 'list',
            'view_mode': 'list',
            'res_model': 'hr.holidays',
            'domain': [('user_id', '=', obj.iduser),('date_to','<',start)],
            'type': 'ir.actions.act_window',
            'target': 'new',
        } 

capacity_planning_before()

## This class contains the informations of tasks without deadline or not started
#
#  
class capacity_planning_without_deadline(osv.osv):
    _name = "capacity.planning.without.deadline"
    _description = "Without deadline"
    _order = "emp" 
    
    _columns = {
        'planning_id': fields.many2one('capacity.planning', 'Planning'),
        'emp' : fields.char('Employe', size=30),
        'departement':fields.char('Department',size=30),
        'nbtask1':fields.integer('Nb tasks without deadline'),
        'nbtask2':fields.integer('Nb tasks not started'),
        'iduser':fields.integer('IDuser'),
        'idresource':fields.integer('IDresource'), 
        'idemp':fields.integer('IDemploye'),
        'idhourofwork':fields.integer('IDhourofwork'),   
    }
    
    ## Method for switch view in task view
    #  @param self The object pointer. 
    #  @param cr The database connection(cursor)
    #  @param uid The id of user performing the operation
    #  @param ids The list of record ids or single integer when there is only one id
    #  @param context The optional dictionary of contextual parameters such as user language
    # 
    def check_task_without_deadline(self,cr,uid,ids,context=None):        
        if context is None:
            context = {}
        obj = self.browse(cr, uid, ids[0], context=context) 
        
        return {
            'name':'Tasks',
            'view_type': 'list',
            'view_mode': 'list',
            'res_model': 'project.task',
            'domain': [('user_id', '=', obj.iduser),'|',('date_deadline','=',None),('state','=','draft')],
            'type': 'ir.actions.act_window',
            'target': 'new',
        } 

capacity_planning_without_deadline()

class planning_generator(osv.osv):
    _name = "planning.generator"
    _description = "Planning generator"
        
    _columns={
        'year':fields.integer('Year',size=4,required=True),
        'in_part':fields.selection([('1','1'),('2','2'),('3','3'),('4','4'),('6','6')],'In part (month)',required=True),
        'sel_department':fields.many2one('hr.department','Department',help="Only if you want just one department for the capacity planning."),
    }
    
    _defaults={
        'year':lambda *a: int(time.strftime('%Y')),
    }
    
    def capacity_generator(self, cr, uid ,ids, context=None):
        temp=self.browse(cr,uid,ids,context)
        date_now = datetime.now()
        i=12/int(temp[0].in_part)
        in_part=int(temp[0].in_part)
        department=temp[0].sel_department.id
        num_mois=1
        y=temp[0].year
        while i>0:
            start=date_now.replace(day=1,month=num_mois,year=y)
            num_mois+=in_part
            if num_mois>12:
                num_mois=1
                y+=1
            end_temp=date_now.replace(day=1,month=num_mois,year=y)
            end=end_temp - timedelta(days=1)
            if department:
                name=str(start.strftime('%d/%m/%Y'))+ " - " +str(end.strftime('%d/%m/%Y')) + " - " + str(temp[0].sel_department.name)
            else:
                name=str(start.strftime('%d/%m/%Y'))+ " - " +str(end.strftime('%d/%m/%Y'))
            self.pool.get('capacity.planning').create(cr, uid, {'name': name,'sel_department':department,'startdate':start,'enddate':end}, context=context)
            i-=1     
            
        return True
    
planning_generator()
