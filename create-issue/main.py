from get_video_name import CheckLectures as CL
from create_issue import Issue

cl = CL()
cl.main()

issue = Issue()
issue.main(cl.videos)
