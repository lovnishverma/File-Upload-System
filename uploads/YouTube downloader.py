#!/usr/bin/env python
# coding: utf-8

# In[1]:


# pip install pytube


# In[1]:


from pytube import YouTube
link = input("Enter the video link : ")
print("Downloading.../")
YouTube(link).streams.first().download()
print("Download Successful")


# In[ ]:




