# (Draft) Usage of IPC support
This version of PixivUtil2 supports messaging system with [ZeroMQ](https://gittehub.com/zeromq).
To enable this feature, specify '--ipc' command line parameter with correct ipc address.
The usage of '--ipc' parameter is '--ipc=<identifier>|<comm socket>|<task socket>'(with identifier) or '--ipc=<comm socket>|<task socket>'(without identifier, default identifier 'PixivUtil2' will be used).
Remind that the first address is for the communication socket, the second is for the task socket.
(Example: '--ipc=tcp://localhost:4048|tcp://localhost:4049')

PixivUtil2 uses ZeroMQ RequestSocket to send messages. Thus, you should use ResponseSocket or RouterSocket to receive and process messages.

Since IPCv2 update, PixivUtil2 uses two socket(Communcation, Task socket) to communicate with any client.

## Communication socket
### HS - Handshake 
* PixivUtil2 -> Client
  1. Identifier and side type(Comm / Task)
* Client -> PixivUtil2
  1. 'Ok' or 'Error'

### TOTAL - Notify total job count
* PixivUtil2 -> Client
  1. Total job count
* Client -> PixivUtil2
  1. 'Ok'

### DL - Download result
* PixivUtil2 -> Client
  1. Image ID
  2. Donload Result (Defined in PixivConstant.py)
* Client -> PixivUtil2
  1. 'Ok'

### TITLE - Window title change request
* PixivUtil2 -> Client
  1. New window title
* Client -> PixivUtil2
  1. 'Ok' or 'Error'

### ERROR - An error occurred
* PixivUtil2 -> Client
  1. Error details
  2. Error stack trace
* Client -> PixivUtil2
  1. 'Ok'

## Task socket
### FFMPEG_REQ - FFmpeg execution request
* PixivUtil2 -> Client
  1. FFmpeg parameter list (not a full command line; FFmpeg executable path is excluded)
* Client -> PixivUtil2
  1. FFmpeg execution task id or 'Error' if an error occurred

### FFMPEG_RET - FFmpeg execution exit code request
* PixivUtil2 -> Client
  1. FFmpeg parameter list (not a full command line; FFmpeg executable path is excluded)
* Client -> PixivUtil2
  1. Exit code or '-1' if there's no FFmpeg task with specified task id

