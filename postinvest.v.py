#Users if this contract get ether and amount of ether is enought variable singup become true for particular address


Users: public({
    project: bool, # why bool? address? -
  #	project_address: address,
    signup: bool, # ?
    }[address])

#Create Projects and set addition data of project's describe

Projects: public({
    projectID: int128,
    project_owner_address: address,
    project_token: address, #(ERC20)?
    IPFSDescribe: bytes32, # address of project in IPFS
    }[int128])

# Depo for user's ethers
ether_depo:public(wei_value)
#Token Darf
darftoken:address(ERC20)
#project's token
projecttoken:address #(ERC20)
#Адресс куда будут перечилятся денежки
beneficiar:address
#id of UserStory
nextUserStoryID:int128
#id of Project
nextProjectID:int128
#id of UserList
nextUserListID:int128

#initial variables
darf2eth: uint256
token_share: decimal
DARF_share: int128
decide_vote: decimal




UserList: ({
   user_address:address, #2do find where used address from Userlist
   summa:wei_value,
   UserStoryID:int128
   }[int128])



UserStory: public({
    projectID:int128,
    user_address:address,
    IPFSHash: bytes32,
    project_accept: bool,
    user_signin:bool, # several users?
    project_signin:bool, #several team members?
    start_date:timestamp,
    duration:timedelta,
    confirm_end_from_project:bool,  #several team members?
    confirm_end_from_user:bool, # several users?
    StoryAmountDarf:uint256,
    StoryAmountTokens:uint256
    }[int128])

#
# 50 grade of rights
GroupRights: public({
    projectID:int128,
    floor_sum:wei_value[50],
    }[int128])

@public
def __init__(darf2eth_start:uint256, token_share_start:decimal, DARF_share_start:int128,decide_vote_start:decimal, thisprojecttoken:address):
    self.darf2eth = darf2eth_start
    self.token_share = token_share_start
    self.DARF_share = DARF_share_start
    self.decide_vote = decide_vote_start
    self.projecttoken = thisprojecttoken

@public
def signup_check() -> bool:
    check_result: bool
    check_result = False
    if self.Users[msg.sender].signup:
        check_result = True
    return check_result

@private
def tokens_and_signin(_to:address,_to_pay:uint256):
     self.darftoken.transfer(_to, _to_pay)
     self.Users[_to].signup = True
     self.ether_depo = self.ether_depo + as_wei_value(_to_pay-_to_pay/100*10,"wei")

@private
def tokens_back(_to:address,_to_pay:uint256):
     self.darftoken.transfer(_to, _to_pay)
     self.ether_depo = self.ether_depo + as_wei_value(_to_pay,"wei")


@public
@payable
def __default__():
    assert as_unitless_number(self.darftoken.balanceOf(self)) < as_unitless_number(msg.value)*self.darf2eth
    check_of_signin: bool = self.Users[msg.sender].signup == True
    token_to_pay: uint256 = as_unitless_number(msg.value)*self.darf2eth
    if check_of_signin:
        self.tokens_back(msg.sender,token_to_pay)
    else:
        self.tokens_and_signin(msg.sender, token_to_pay)


@private
def sendEther(_to:address,_value:uint256):
    send(_to, as_wei_value(_value/self.darf2eth,'wei'))
    self.ether_depo = self.ether_depo - as_wei_value(_value/self.darf2eth,'wei')
@private
def sendEtherWithSing(_to:address,_value:uint256):
    self.Users[msg.sender].signup = True
    send(_to, as_wei_value((_value-10)/self.darf2eth,'wei'))

@public
@payable
def exchangeDARF2ETH (sum_DARF:wei_value):
    if (self.darftoken.balanceOf(msg.sender)>as_unitless_number(sum_DARF)) and (self.balance>sum_DARF*self.darf2eth):
        if self.Users[msg.sender].signup : #check_result:
            self.sendEther(msg.sender,as_unitless_number(msg.value))
        else:
            self.sendEtherWithSing(msg.sender,as_unitless_number(msg.value))


@public
def get_ballance_of_depo() -> uint256(wei):
    return self.ether_depo

@public
def create_project(owner_address: address,token:address,IPFSDescribe:bytes32):
    assert self.Users[msg.sender].signup == True
    assert self.Users[msg.sender].project == True
    ProjectID: int128 = self.nextProjectID
    self.Projects[ProjectID] = {projectID:ProjectID, project_owner_address:owner_address, project_token:token, IPFSDescribe:IPFSDescribe}
    self.nextProjectID = ProjectID + 1



# # set and check grade of rights for project
# # level of access based on amount  of project's token on user's address.
# # f.e. 10 tokens - means "1"st level -  trafficlight spectator,
# # 100 tokens - "2"nd level  - reports analyser,
# # 1000 tokens - "3"td level - transaction auditor
# # 10000 tokens - "4"th level - scrum participator
# # 100000 tokens - "5"th - team member
# # 1000000 tokens - "6"s level- manager
# # 10000000 tokens - "7"s lev - top manager
# # or another grade list
# # 100 grades available
# # 2do: this grades'd be mapped with access right in ERP


# @public
# def setrights(ProjectID:int128,index:int128,floor_sum:uint256) :
#     assert self.Projects[ProjectID].project_owner_address != msg.sender
#     self.rights_set = grade_rights

# @public
# def checkrights(): #check access rights to project
#     tokenbalance: wei
#     self.tokenbalance = self.projecttoken.balanceOf(msg.sender)
#     for grade in range(10): #
#         if self.rights_set(grade).floor_sum < self.tokenbalance:
#             return grade
    # 2DO  !!! log wrong grade table
    # assert
    # d need this?


@public
def change_project_info(ProjectID:int128, NewIPFSDescribe:bytes32):
    assert self.Projects[ProjectID].project_owner_address != msg.sender
    self.Projects[ProjectID].IPFSDescribe = NewIPFSDescribe

@public
def start_user_story(projectID:int128,IPFSHash:bytes32,storyAmountDarf:uint256): # initiation of userstory
      # Для регистрации истории он посылает на смарт-контракт символическую сумму 1 ДАРФ

    # В смарт-контракте фиксируется адрес (ID) истории
    #  deploy new u instance ?
    assert self.Users[msg.sender].signup == True
    UserStoryID: int128 = self.nextUserStoryID
    self.UserStory[UserStoryID] = {projectID:projectID,
                                  IPFSHash:IPFSHash,
                                  project_accept: False,
                                  user_address:msg.sender,
                                  user_signin:False,
                                  project_signin:False,
                                  start_date:0,
                                  duration:0,
                                  confirm_end_from_project:False,
                                  confirm_end_from_user:False,
                                  StoryAmountDarf:storyAmountDarf,
                                  StoryAmountTokens:0
                                  }
    self.nextUserStoryID = UserStoryID + 1

@public
def accept_user_story_from_project(UserStoryID:int128): # team accepts userstory for work from backlog
    ProjectID: int128 = self.UserStory[UserStoryID].projectID
    assert self.Projects[ProjectID].project_owner_address != msg.sender
    self.UserStory[UserStoryID].project_accept = True

@public
def sign_in_user_story_from_user(UserStoryID:int128): # investors signup userstory when negotiations finished
  # investors  send DARF to userstory if agree

    ProjectID: int128 = self.UserStory[UserStoryID].projectID
    assert self.UserStory[UserStoryID].user_address != msg.sender
    if self.UserStory[UserStoryID].user_signin != True: # really?
        self.UserStory[UserStoryID].user_signin = True
        if  self.UserStory[UserStoryID].project_signin :
            self.UserStory[UserStoryID].start_date = block.timestamp



@public
def sign_in_user_story_from_project(UserStoryID:int128): # team signup userstory when negotiations finished
    ProjectID: int128 = self.UserStory[UserStoryID].projectID
    assert self.Projects[ProjectID].project_owner_address != msg.sender
    if  self.UserStory[UserStoryID].project_signin != True : # 2do: refactor?
        self.UserStory[UserStoryID].project_signin = True
        if self.UserStory[UserStoryID].user_signin :
            self.UserStory[UserStoryID].start_date = block.timestamp


@public
def confirm_end_from_project(UserStoryID:int128): # team finished the userstory and initiate acceptance from investors
    ProjectID: int128 = self.UserStory[UserStoryID].projectID
    assert self.Projects[ProjectID].project_owner_address != msg.sender
    assert block.timestamp < self.UserStory[UserStoryID].start_date +self.UserStory[UserStoryID].duration
    self.UserStory[UserStoryID].confirm_end_from_project = True

@public
def confirm_end_from_user(UserStoryID:int128): # investors accept work
    assert self.UserStory[UserStoryID].user_address != msg.sender
    ProjectID: int128 = self.UserStory[UserStoryID].projectID
    project_address: address = self.Projects[ProjectID].project_owner_address
    storyAmountDarf: uint256 = self.UserStory[UserStoryID].StoryAmountDarf/100*convert(self.DARF_share,'uint256')
    FullStoryAmountDarf: uint256 = self.UserStory[UserStoryID].StoryAmountDarf/100*convert(self.DARF_share,'uint256')
    # tokens 2 user

    self.UserStory[UserStoryID].confirm_end_from_user = True
    self.darftoken.transfer(project_address, as_unitless_number(storyAmountDarf))
    self.ether_depo = self.ether_depo - as_wei_value(FullStoryAmountDarf/500, 'wei')
    # 5% tokens & ETH to us

# if team fails... deadline is broken, undersing LT then 50% of sum and one on investors initiate refunding
@public
def userstory_fail_refund (UserStoryID: int128):
    assert self.UserStory[UserStoryID].user_address != msg.sender
    if block.timestamp > self.UserStory[UserStoryID].start_date + self.UserStory[UserStoryID].duration : #deadline is broken
        if self.UserStory[UserStoryID].confirm_end_from_user != True:
            # 2DO what do u mean here?
            return # ?? or...
@public
def change_conditions (darf2Eth:uint256, TokenShare:decimal, DARFShare:int128):
    assert self.beneficiar != msg.sender
    self.darf2eth = darf2Eth
    self.token_share = TokenShare
    self.DARF_share = DARFShare

# # the end
