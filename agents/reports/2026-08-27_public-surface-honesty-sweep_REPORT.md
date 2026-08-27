# Report: Public-Surface Honesty Sweep

**Brief:** `agents/briefs/2026-08-27_public-surface-honesty-sweep.md`  
**Date:** 2026-08-27  
**Auditor:** Gemini (Antigravity)

---

## What I changed

```diff
diff --git a/blog-ggplot2-timeseries.html b/blog-ggplot2-timeseries.html
index 6f08f42..28e66ad 100644
--- a/blog-ggplot2-timeseries.html
+++ b/blog-ggplot2-timeseries.html
@@ -80,7 +80,7 @@ ggplot(data = plankton_df,           # 1. Data
 library(lubridate)
 
 # Load and prepare the data
-plankton_df &lt;- read_csv("hamocc_plankton_output.csv") %&gt;%
+plankton_df &lt;- read_csv("plankton_output.csv") %&gt;%
   mutate(date = ymd(date)) %&gt;%
   filter(date &gt;= "2015-01-01", date &lt;= "2020-12-31")
```

---

## Checkpoint output

### Checkpoint 1

```powershell
PS C:\Users\Admin\Documents\thejusmahajan.github.io> git diff --numstat blog-ggplot2-timeseries.html
warning: in the working copy of 'blog-ggplot2-timeseries.html', LF will be replaced by CRLF the next time Git touches it
1	1	blog-ggplot2-timeseries.html

PS C:\Users\Admin\Documents\thejusmahajan.github.io> git diff blog-ggplot2-timeseries.html
warning: in the working copy of 'blog-ggplot2-timeseries.html', LF will be replaced by CRLF the next time Git touches it
diff --git a/blog-ggplot2-timeseries.html b/blog-ggplot2-timeseries.html
index 6f08f42..28e66ad 100644
--- a/blog-ggplot2-timeseries.html
+++ b/blog-ggplot2-timeseries.html
@@ -80,7 +80,7 @@ ggplot(data = plankton_df,           # 1. Data
 library(lubridate)
 
 # Load and prepare the data
-plankton_df &lt;- read_csv("hamocc_plankton_output.csv") %&gt;%
+plankton_df &lt;- read_csv("plankton_output.csv") %&gt;%
   mutate(date = ymd(date)) %&gt;%
   filter(date &gt;= "2015-01-01", date &lt;= "2020-12-31")
 

PS C:\Users\Admin\Documents\thejusmahajan.github.io> Select-String -Path *.html -Pattern "hamocc" -CaseSensitive:$false
```

### Checkpoint 2

```powershell
PS C:\Users\Admin\Documents\thejusmahajan.github.io> Get-ChildItem -Recurse -Include *.html,*.md,*.js,*.css |
>>   Where-Object { $_.FullName -notmatch '\\\.git\\' } |
>>   Select-String -Pattern 'hamocc','icon-o','eerie','levante','dkrz' -CaseSensitive:$false
```

### Checkpoint 3

```powershell
PS C:\Users\Admin\Documents\thejusmahajan.github.io> Select-String -Path C:\Users\Admin\Documents\thejusmahajan.github.io\experience.html -Pattern '2012','2009','Calicut' -Context 1,1

  C:\Users\Admin\Documents\thejusmahajan.github.io\experience.html:239:                    <h3 class="font-bold text-gray-900 text-lg mb-2">M.Sc. in Physics</h3>
> C:\Users\Admin\Documents\thejusmahajan.github.io\experience.html:240:                    <p class="text-sky-600 font-medium text-sm mb-1">National Institute of Technology Calicut, India</p>
  C:\Users\Admin\Documents\thejusmahajan.github.io\experience.html:241:                    <p class="text-gray-700 font-semibold text-sm mb-1">CGPA: 8.71/10</p>
> C:\Users\Admin\Documents\thejusmahajan.github.io\experience.html:242:                    <p class="text-gray-500 text-sm">2012 - 2014</p>
  C:\Users\Admin\Documents\thejusmahajan.github.io\experience.html:243:                </div>
  C:\Users\Admin\Documents\thejusmahajan.github.io\experience.html:245:                    <h3 class="font-bold text-gray-900 text-lg mb-2">B.Sc. in Physics</h3>
> C:\Users\Admin\Documents\thejusmahajan.github.io\experience.html:246:                    <p class="text-sky-600 font-medium text-sm mb-1">University of Calicut, India</p>
> C:\Users\Admin\Documents\thejusmahajan.github.io\experience.html:247:                    <p class="text-gray-500 text-sm">2009 - 2012</p>
  C:\Users\Admin\Documents\thejusmahajan.github.io\experience.html:248:                </div>

PS C:\Users\Admin\Documents\thejusmahajan.github.io> Select-String -Path C:\Users\Admin\Documents\job_search\applications\hereon_aeon_up\cv_hereon_aeon_up.tex -Pattern '2012','2009'

C:\Users\Admin\Documents\job_search\applications\hereon_aeon_up\cv_hereon_aeon_up.tex:237:             {07/2012 - 12/2014}
C:\Users\Admin\Documents\job_search\applications\hereon_aeon_up\cv_hereon_aeon_up.tex:245:             {06/2009 - 04/2012}
```

### Checkpoint 4a

```powershell
PS C:\Users\Admin\Documents\thejusmahajan.github.io> Test-Path C:\Users\Admin\Documents\job_search\linkedin_profile.txt
False
```

---

## LinkedIn findings

LinkedIn audit blocked — `linkedin_profile.txt` not present. Thejus needs to paste his profile text into it: headline, About section, and every Experience and Education entry.

---

## Deviations

None

---

## Opinions

None
