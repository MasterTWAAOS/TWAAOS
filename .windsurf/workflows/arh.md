---
description: Arhitecture respect
---

Doing all this keep in mind the arhitecture of the project, so look at the arhitecture of the backend and respect it, likewise for the frontend. A little description would be that i use in the backend controllers, coupled to services only, by interfaces. And the services are coupled to repository only by interfaces also. And in the frontend exists an arhitecture as well, so analyse it and keep it in mind doing any change that i mentioned previously.
And also keep in mind that whenever you are going to make changes to a .vue file, to make smaller changes at a time, because the files are very big and your tool call will fail if you make big changes at once.