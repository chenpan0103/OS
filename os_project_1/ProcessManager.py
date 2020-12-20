
class PCB():
    def __init__(self,pid,cpu,mem,open_files,other_sources,status,
                 parent,children,priority,bl_resource):
        self.pid=pid
        self.cpu=cpu
        self.mem=mem
        self.open_files=open_files
        self.other_sources=other_sources
        self.status=status
        self.parent=parent
        self.children=children
        self.priority=priority
        self.bl_resource=bl_resource

class ProcessManager():
    ## 初始化资源，ready队列，block队列，running进程......
    def __init__(self):
        self.resource={"R1":1,"R2":2,"R3":3,"R4":4}
        self.maxresource={"R1":1,"R2":2,"R3":3,"R4":4}
        self.ready=[[],[],[]]
        self.block={"R1":[],"R2":[],"R3":[],"R4":[]}
        self.block_list=[]
        self.running=None
        self.processdic={}

    # 打印当前运行的进程
    def Print(self):
        print("process {} is running.".format(self.running.pid))

    ##创建根进程
    def init(self):
        newPCB = PCB(pid="init", cpu=None, mem=None, open_files=None,
                     other_sources={"R1":0,"R2":0,"R3":0,"R4":0},
                     status="running",parent=self.running,children=[],
                     priority=0,bl_resource={"R1":0,"R2":0,"R3":0,"R4":0})
        self.running=newPCB
        self.processdic[newPCB.pid]=newPCB
        print("init process is running")
        # self.Scheduler()

    ## 创建新进程
    def create(self,pid,priority):
        newPCB=PCB(pid=pid,cpu=None,mem=None,open_files=None,
                   other_sources={"R1":0,"R2":0,"R3":0,"R4":0},status="ready",parent=self.running,
                   children=[],priority=priority,bl_resource={"R1":0,"R2":0,"R3":0,"R4":0})
        self.processdic[newPCB.pid]=newPCB
        self.running.children.append(newPCB)
        newPCB.parent=self.running
        # print(newPCB.priority)
        if newPCB.priority <= self.running.priority:
            self.ready[priority].append(newPCB)
        else:
            self.running.status="ready"
            newPCB.status="running"
            self.ready[self.running.priority].append(self.running)
            self.running=newPCB
        self.Print()
        # self.Scheduler()

    def scheduler_ready(self):
        for i in range(2,-1,-1):
            if len(self.ready[i])!=0:
                return self.ready[i].pop(0)
        return None
    def ready_is_empty(self):
        if len(self.ready[2])==0 and len\
                    (self.ready[1])==0 and len(self.ready[0])==0:
            return True
        else:
            return False
    ## 请求资源
    def request(self,rname,rnum):
        cur_num=self.resource[rname]
        max_num=self.maxresource[rname]
        if max_num < rnum:
            print("超出最大资源量!")
        elif cur_num < rnum:
            self.running.status="blocked"
            self.running.bl_resource[rname]+=rnum
            self.block[rname].append(self.running)
            self.block_list.append(self.running)
            newPCB = self.scheduler_ready()
            newPCB.status="running"
            print("process {} is running. process {} is blocked.".
                  format(newPCB.pid,self.running.pid))
            self.running = newPCB
        else:
            self.resource[rname]-=rnum
            self.running.other_sources[rname]+=rnum
            print("process {} requests {} {}".format(self.running.pid,
                                                     rnum,rname))

    ## 进程释放资源
    def release(self,pid,rname):
        tagPCB=self.processdic[pid]
        rnum=tagPCB.other_sources[rname]
        # print("rnum",rnum)
        tagPCB.other_sources[rname]-=rnum
        self.resource[rname]+=rnum

    ## show list
    def list_ready(self):
        for i in range(3):
            str="{}: ".format(i)
            for i in self.ready[i]:
                str=str+i.pid+"-"
            print(str[:-1])

    def list_block(self):
        for k in self.block:
            str="{} ".format(k)
            for pcb in self.block[k]:
                str=str+pcb.pid+"-"
            print(str[:-1])

    def list_res(self):
        for k in self.resource:
            print("{} {}".format(k,self.resource[k]))

    ## 删除进程
    def destroy(self,pid):
        """
        1. 删除子进程
        2. 释放资源
        3. 更新相关的子进程
        4. 检查是否有block的进程被唤醒(需先检查删除进程是否为运行）
        """
        tagPCB=self.processdic[pid]


        ## 释放资源
        self.release(pid, "R1")
        self.release(pid, "R2")
        self.release(pid, "R3")
        self.release(pid, "R4")

        ## 从processdic、ready、block删除进程及子进程
        ## 与此同时，应该被删除进程的父进程的children
        parent = self.processdic[pid].parent
        parent.children.remove(self.processdic[pid])

        del self.processdic[pid]
        for i in self.ready[tagPCB.priority]:
            if i.pid == pid:
                self.ready[tagPCB.priority].remove(i)
        for i in self.block:
            for item in self.block[i]:
                if item.pid == pid:
                    self.block[i].remove(item)
                    self.block_list.remove(item)


        ## 唤醒block中的进程,这里只考虑一个进程最多只被一种资源堵塞的情况
        ## 对于占有多个资源的释放应该考虑堵塞进程的优先顺序，需设立一个标志来判断
        ## 不同资源间的堵塞时间顺序
        sign = False
        for pcb in self.block_list:
            """
            遍历找出释放资源后可满足运行的第一个进程，该实验局限在
            一次最多请求一类资源
            """
            for k in self.block:
                # print(self.block[k])
                if sign==True: break
                if pcb in self.block[k] and self.resource[k]>=pcb.bl_resource[k]:
                    self.block_list.remove(pcb)
                    self.block[k].remove(pcb)
                    # self.running = pcb
                    if tagPCB==self.running:
                        pcb.status="running"
                        self.running=pcb
                    else:
                        pcb.status="ready"
                        self.ready[pcb.priority].append(pcb)
                    print("release {}. wake up processs {}.".format(k,pcb.pid))
                    sign=True
        if sign == False and tagPCB.status=="running":
            if self.ready_is_empty():
                print("There is no process.")
            elif len(self.ready[tagPCB.priority])==0:
                newPCB=self.ready[tagPCB.priority-1].pop(0)
                self.running=newPCB
                self.running.status="running"
            else:
                self.running = self.scheduler_ready()
                self.running.status = "running"

        ## 递归处理
        if len(tagPCB.children) != 0:
            for child in tagPCB.children:
               self.destroy(child.pid)

    ## 模拟时间中断
    def timeout(self):
        cur_priorioty=self.running.priority
        if len(self.ready[cur_priorioty])==0:
            self.Print()
        else:
            changePCB=self.scheduler_ready()
            if changePCB != None:
                tmpPCB = self.running
                self.running.status="ready"
                self.ready[tmpPCB.priority].append(tmpPCB)
                changePCB.status="running"
                self.running = changePCB
                print("process {} is running. process {} is ready.".
                      format(self.running.pid, tmpPCB.pid))
            else:
                self.Print()

     ## 打印给定进程的信息
    def printPCB(self,pid):
        tagPCB=self.processdic[pid]
        parent=tagPCB.parent
        children=tagPCB.children
        clist=[item.pid for item in children]
        # print("print the information of the  )
        print("Pid:{} Priority:{} Parent:{} Children"
              ":{} Status:{} Occupied_Resource:"
              "{} ".format(tagPCB.pid,tagPCB.priority,tagPCB.parent.pid,
                           clist,tagPCB.status,tagPCB.other_sources))

import shlex
def Test_shell(filepath):
    manager=ProcessManager()
    with open(filepath,"r") as f:
        for cmd in f.readlines():

            cmd=shlex.split(cmd)
            # print(cmd)
            while cmd!="q":
                if cmd[0] == "init":
                    manager.init()
                elif cmd[0] == "cr":
                    manager.create(cmd[1], int(cmd[2]))
                elif cmd[0] == "req":
                    manager.request(cmd[1], int(cmd[2]))
                elif cmd[0] == "de":
                    manager.destroy(cmd[1])
                elif cmd[0] == "to":
                    manager.timeout()
                elif cmd[0] == "list" and cmd[1] == "ready":
                    manager.list_ready()
                elif cmd[0] == "list" and cmd[1] == "block":
                    manager.list_block()
                elif cmd[0] == "list" and cmd[1] == "res":
                    manager.list_res()
                elif cmd[0] == "pr":
                    manager.printPCB(cmd[1])
                break

Test_shell("./cmd.txt")

# manager=ProcessManager()
# manager.init()
# manager.create("x",1)
# manager.create("p",1)
# manager.create("q",1)
# manager.create("r",1)
# manager.list_ready()
# manager.timeout()
# manager.request("R2",1)
# manager.timeout()
# manager.request("R3",3)
# manager.timeout()
# manager.request("R4",3)
# manager.list_res()
# manager.timeout()
# manager.timeout()
# manager.request("R3",1)
# manager.request("R4",2)
# manager.request("R2",2)
# manager.list_block()
# manager.timeout()
# manager.destroy("q")
# manager.timeout()
# # manager.list_res()
# # manager.list_block()
# manager.timeout()
# for k in manager.processdic:
#     print(manager.processdic[k].pid,manager.processdic[k].other_sources)





            









