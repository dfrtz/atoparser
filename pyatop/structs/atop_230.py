"""Structs and definitions used serialize/deserialize ATOP statistics directly from log files.

Structs are declared in a way that will help provide as close to a 1 to 1 match as possible for debuggability
and maintenance. The _fields_ of every struct match their original name, however the struct names have been updated
to match python CamelCase standards. Each struct includes the following to help identify the original source:
    C Name: utsname
    C Location: sys/utsname.h

Struct ordering and visual whitespace in the _fields_ are left to help match the original source in readability.
If structs match exactly from a previous version, they are reused via aliasing.

See https://github.com/Atoptool/atop for more information and references to the C process source code.
Using schemas and structs from ATOP 2.30.
"""

import ctypes

from pyatop.structs import atop_126


# Disable the following pylint warnings to allow the variables and classes to match the style from the C.
# This helps with maintainability and cross-referencing.
# pylint: disable=invalid-name,too-few-public-methods

# Definitions from time.h
time_t = ctypes.c_long

# Definitions from atop.h
count_t = ctypes.c_longlong
ACCTACTIVE = 0x00000001
PATCHSTAT = 0x00000002
IOSTAT = 0x00000004
PATCHACCT = 0x00000008

# Definitions from sys/types.h
off_t = ctypes.c_long

# Definitions from photoproc.h
PNAMLEN = 15
CMDLEN = 255

# Definitions from photosyst.h
MAXCPU = 2048
MAXDSK = 1024
MAXLVM = 2048
MAXMDD = 256
MAXINTF = 128
MAXCONTAINER = 128
MAXNFSMOUNT = 64
MAXDKNAM = 32


UTSName = atop_126.UTSName


class Header(ctypes.Structure):
    """Top level struct to describe information about the system running ATOP and the log file itself.

    Field descriptions from atop:
        aversion   Creator atop version with MSB.
        future1    Can be reused.
        future2    Can be reused.
        rawheadlen Length of struct rawheader.
        rawreclen  Length of struct rawrecord.
        hertz      Clock interrupts per second.
        sfuture[6] Future use.
        sstatlen   Length of struct sstat.
        tstatlen   Length of struct tstat.
        utsname    Info about this system.

    C Name: rawheader
    C Location: rawlog.c
    """

    _fields_ = [
        ('magic', ctypes.c_uint),

        ('aversion', ctypes.c_ushort),
        ('future1', ctypes.c_ushort),
        ('future2', ctypes.c_ushort),
        ('rawheadlen', ctypes.c_ushort),
        ('rawreclen', ctypes.c_ushort),
        ('hertz', ctypes.c_ushort),
        ('sfuture', ctypes.c_ushort * 6),
        ('sstatlen', ctypes.c_uint),
        ('tstatlen', ctypes.c_uint),
        ('utsname', UTSName),
        ('cfuture', ctypes.c_char * 8),

        ('pagesize', ctypes.c_uint),
        ('supportflags', ctypes.c_int),
        ('osrel', ctypes.c_int),
        ('osvers', ctypes.c_int),
        ('ossub', ctypes.c_int),
        ('ifuture', ctypes.c_int * 6),
    ]

    def check_compatibility(self) -> None:
        """Verify if the loaded values are compatible with this header version.

        Raises:
            ValueError if not compatible.
        """
        compatible = [
            self.sstatlen == ctypes.sizeof(SStat),
            self.tstatlen == ctypes.sizeof(TStat),
            self.rawheadlen == ctypes.sizeof(Header),
            self.rawreclen == ctypes.sizeof(Record),
        ]
        if not all(compatible):
            raise ValueError(f'File has incompatible atop format. Struct length evaluations: {compatible}')

    def get_version(self) -> float:
        """Convert the raw version into a semantic version.

        Returns:
            version: The final major.minor version from the header aversion.
        """
        major = (self.aversion >> 8) & 0x7f
        minor = self.aversion & 0xff
        version = float(f'{major}.{minor}')
        return version


class Record(ctypes.Structure):
    """Top level struct to describe basic process information, and the following SStat and TStat structs.

    Field descriptions from atop:
        curtime    Current time (epoch).
        flags      Various flags.
        sfuture[3] Future use.
        scomplen   Length of compressed sstat.
        pcomplen   Length of compressed tstats.
        interval   Interval (number of seconds).
        ndeviat    Number of tasks in list.
        nactproc   Number of processes in list.
        ntask      Total number of tasks.
        totproc    Total number of processes.
        totrun     Number of running  threads.
        totslpi    Number of sleeping threads(S).
        totslpu    Number of sleeping threads(D).
        totzomb    Number of zombie processes.
        nexit      Number of exited processes.
        noverflow  Number of overflow processes.
        ifuture[6] Future use.

    C Name: rawrecord
    C Location: rawlog.c
    """

    _fields_ = [
        ('curtime', time_t),

        ('flags', ctypes.c_ushort),
        ('sfuture', ctypes.c_ushort * 3),

        ('scomplen', ctypes.c_uint),
        ('pcomplen', ctypes.c_uint),
        ('interval', ctypes.c_uint),
        ('ndeviat', ctypes.c_uint),
        ('nactproc', ctypes.c_uint),
        ('ntask', ctypes.c_uint),
        ('totproc', ctypes.c_uint),
        ('totrun', ctypes.c_uint),
        ('totslpi', ctypes.c_uint),
        ('totslpu', ctypes.c_uint),
        ('totzomb', ctypes.c_uint),
        ('nexit', ctypes.c_uint),
        ('noverflow', ctypes.c_uint),
        ('ifuture', ctypes.c_uint * 6),
    ]


class MemStat(ctypes.Structure):
    """Embedded struct to describe basic memory information.

    C Name: memstat
    C Location: photosyst.h
    C Parent: sstat
    """

    _fields_ = [
        ('physmem', count_t),
        ('freemem', count_t),
        ('buffermem', count_t),
        ('slabmem', count_t),
        ('cachemem', count_t),
        ('cachedrt', count_t),

        ('totswap', count_t),
        ('freeswap', count_t),

        ('pgscans', count_t),
        ('pgsteal', count_t),
        ('allocstall', count_t),
        ('swouts', count_t),
        ('swins', count_t),

        ('commitlim', count_t),
        ('committed', count_t),

        ('shmem', count_t),
        ('shmrss', count_t),
        ('shmswp', count_t),

        ('slabreclaim', count_t),

        ('tothugepage', count_t),
        ('freehugepage', count_t),
        ('hugepagesz', count_t),

        ('vmwballoon', count_t),

        ('cfuture', count_t * 8),
    ]


FreqCnt = atop_126.FreqCnt


class PerCPU(ctypes.Structure):
    """Embedded struct to describe per processor usage information.

    C Name: percpu
    C Location: photosyst.h
    C Parent: cpustat
    """

    _fields_ = [
        ('cpunr', ctypes.c_int),
        ('stime', count_t),
        ('utime', count_t),
        ('ntime', count_t),
        ('itime', count_t),
        ('wtime', count_t),
        ('Itime', count_t),
        ('Stime', count_t),
        ('steal', count_t),
        ('guest', count_t),
        ('freqcnt', FreqCnt),
        ('cfuture', count_t * 4),
    ]


class CPUStat(ctypes.Structure):
    """Embedded struct to describe basic overall processor information.

    C Name: cpustat
    C Location: photosyst.h
    C Parent: sstat
    """

    _fields_ = [
        ('nrcpu', count_t),
        ('devint', count_t),
        ('csw', count_t),
        ('nprocs', count_t),
        ('lavg1', ctypes.c_float),
        ('lavg5', ctypes.c_float),
        ('lavg15', ctypes.c_float),
        ('cfuture', count_t * 4),

        ('all', PerCPU),
        ('cpu', PerCPU * MAXCPU)
    ]


class PerDSK(ctypes.Structure):
    """Embedded struct to describe per disk information.

    C Name: perdsk
    C Location: photosyst.h
    C Parent: dskstat
    """

    _fields_ = [
        ('name', ctypes.c_char * MAXDKNAM),
        ('nread', count_t),
        ('nrsect', count_t),
        ('nwrite', count_t),
        ('nwsect', count_t),
        ('io_ms', count_t),
        ('avque', count_t),
        ('cfuture', count_t * 4),
    ]


class DSKStat(ctypes.Structure):
    """Embedded struct to describe overall disk information.

    C Name: dskstat
    C Location: photosyst.h
    C Parent: sstat
    """

    _fields_ = [
        ('ndsk', ctypes.c_int),
        ('nmdd', ctypes.c_int),
        ('nlvm', ctypes.c_int),
        ('dsk', PerDSK * MAXDSK),
        ('mdd', PerDSK * MAXMDD),
        ('lvm', PerDSK * MAXLVM),
    ]


class PerIntf(ctypes.Structure):
    """Embedded struct to describe per interface statistics.

    C Name: perintf
    C Location: photosyst.h
    C Parent: intfstat
    """

    _fields_ = [
        ('name', ctypes.c_char * 16),

        ('rbyte', count_t),
        ('rpack', count_t),
        ('rerrs', count_t),
        ('rdrop', count_t),
        ('rfifo', count_t),
        ('rframe', count_t),
        ('rcompr', count_t),
        ('rmultic', count_t),
        ('rfuture', count_t * 4),

        ('sbyte', count_t),
        ('spack', count_t),
        ('serrs', count_t),
        ('sdrop', count_t),
        ('sfifo', count_t),
        ('scollis', count_t),
        ('scarrier', count_t),
        ('scompr', count_t),
        ('sfuture', count_t * 4),

        ('type', ctypes.c_char),
        ('speed', ctypes.c_long),
        ('speedp', ctypes.c_long),
        ('duplex', ctypes.c_char),
        ('cfuture', count_t * 4),
    ]


class IntfStat(ctypes.Structure):
    """Embedded struct to describe overall interface statistics.

    C Name: intfstat
    C Location: photosyst.h
    C Parent: sstat
    """

    _fields_ = [
        ('nrintf', ctypes.c_int),
        ('intf', PerIntf * MAXINTF),
    ]


class PerNFSMount(ctypes.Structure):
    """Embedded struct to describe per NFS mount statistics.

    C Name: pernfsmount
    C Location: photosyst.h
    C Parent: nfsmounts
    """

    _fields_ = [
        ('name', ctypes.c_char * 128),
        ('age', count_t),

        ('bytesread', count_t),
        ('byteswrite', count_t),
        ('bytesdread', count_t),
        ('bytesdwrite', count_t),
        ('bytestotread', count_t),
        ('bytestotwrite', count_t),
        ('pagesmread', count_t),
        ('pagesmwrite', count_t),

        ('future', count_t * 8),
    ]


class Server(ctypes.Structure):
    """Embedded struct to describe NFS server information from the 'NFS' parseable.

    C Name: server
    C Location: photoproc.h
    C Parent: nfsstat
    """

    _fields_ = [
        ('netcnt', count_t),
        ('netudpcnt', count_t),
        ('nettcpcnt', count_t),
        ('nettcpcon', count_t),

        ('rpccnt', count_t),
        ('rpcbadfmt', count_t),
        ('rpcbadaut', count_t),
        ('rpcbadcln', count_t),

        ('rpcread', count_t),
        ('rpcwrite', count_t),

        ('rchits', count_t),
        ('rcmiss', count_t),
        ('rcnoca', count_t),

        ('nrbytes', count_t),
        ('nwbytes', count_t),

        ('future', count_t * 8),
    ]


class Client(ctypes.Structure):
    """Embedded struct to describe NFS client information from the 'NFC' parseable.

    C Name: client
    C Location: photoproc.h
    C Parent: nfsstat
    """

    _fields_ = [
        ('rpccnt', count_t),
        ('rpcretrans', count_t),
        ('rpcautrefresh', count_t),

        ('rpcread', count_t),
        ('rpcwrite', count_t),

        ('future', count_t * 8),
    ]


class NFSMounts(ctypes.Structure):
    """Embedded struct to describe NFS mount information from the 'NFM' parseable.

    C Name: mfsmounts
    C Location: photoproc.h
    C Parent: nfsstat
    """

    _fields_ = [
        ('nrmounts', ctypes.c_int),
        ('pernfsmount', PerNFSMount * MAXNFSMOUNT)
    ]


class NFSStat(ctypes.Structure):
    """Embedded struct to describe NFS subsystem.

    C Name: nfstat
    C Location: photosyst.h
    C Parent: sstat
    """

    _fields_ = [
        ('server', Server),
        ('client', Client),
        ('nfsmounts', NFSMounts),
    ]


class PerContainer(ctypes.Structure):
    """Embedded struct to describe per container statistics.

    C Name: percontainer
    C Location: photosyst.h
    C Parent: constat
    """

    _fields_ = [
        ('ctid', ctypes.c_ulong),
        ('numproc', ctypes.c_ulong),

        ('system', count_t),
        ('user', count_t),
        ('nice', count_t),
        ('uptime', count_t),

        ('physpages', count_t),
    ]


class ContStat(ctypes.Structure):
    """Embedded struct to describe container subsystem.

    C Name: contstat
    C Location: photosyst.h
    C Parent: sstat
    """

    _fields_ = [
        ('nrcontainer', ctypes.c_int),
        ('cont', PerContainer * MAXCONTAINER),
    ]


WWWStat = atop_126.WWWStat


IPv4Stats = atop_126.IPv4Stats


ICMPv4Stats = atop_126.ICMPv4Stats


UDPv4Stats = atop_126.UDPv4Stats


TCPStats = atop_126.TCPStats


IPv6Stats = atop_126.IPv6Stats


ICMPv6Stats = atop_126.ICMPv6Stats


UDPv6Stats = atop_126.UDPv6Stats


NETStat = atop_126.NETStat


class SStat(ctypes.Structure):
    """Top level struct to describe various subsystems.

    C Name: sstat
    C Location: photosyst.h
    """

    _fields_ = [
        ('cpu', CPUStat),
        ('mem', MemStat),
        ('net', NETStat),
        ('intf', IntfStat),
        ('dsk', DSKStat),
        ('nfs', NFSStat),
        ('cfs', ContStat),

        ('www', WWWStat),
    ]


class GEN(ctypes.Structure):
    """Embedded struct to describe a single process' general information from the 'GEN' parseable.

    C Name: gen
    C Location: photoproc.h
    C Parent: tstat
    """

    _fields_ = [
        ('tgid', ctypes.c_int),
        ('pid', ctypes.c_int),
        ('ppid', ctypes.c_int),
        ('ruid', ctypes.c_int),
        ('euid', ctypes.c_int),
        ('suid', ctypes.c_int),
        ('fsuid', ctypes.c_int),
        ('rgid', ctypes.c_int),
        ('egid', ctypes.c_int),
        ('sgid', ctypes.c_int),
        ('fsgid', ctypes.c_int),
        ('nthr', ctypes.c_int),
        ('name', ctypes.c_char * (PNAMLEN + 1)),
        ('isproc', ctypes.c_char),
        ('state', ctypes.c_char),
        ('excode', ctypes.c_int),
        ('btime', time_t),
        ('elaps', time_t),
        ('cmdline', ctypes.c_char * (CMDLEN + 1)),
        ('nthrslpi', ctypes.c_int),
        ('nthrslpu', ctypes.c_int),
        ('nthrrun', ctypes.c_int),

        ('ctid', ctypes.c_int),
        ('vpid', ctypes.c_int),

        ('wasinactive', ctypes.c_int),

        ('container', ctypes.c_char * 16),
    ]


CPU = atop_126.CPU


DSK = atop_126.DSK


class MEM(ctypes.Structure):
    """Embedded struct to describe a single process' memory usage from the 'MEM' parseable.

    C Name: mem
    C Location: photoproc.h
    C Parent: tstat
    """

    _fields_ = [
        ('minflt', count_t),
        ('majflt', count_t),
        ('vexec', count_t),
        ('vmem', count_t),
        ('rmem', count_t),
        ('pmem', count_t),
        ('vgrow', count_t),
        ('rgrow', count_t),
        ('vdata', count_t),
        ('vstack', count_t),
        ('vlibs', count_t),
        ('vswap', count_t),
        ('cfuture', count_t * 4),
    ]


class NET(ctypes.Structure):
    """Embedded struct to describe a single process' network usage from the 'NET' parseable.

    C Name: net
    C Location: photoproc.h
    C Parent: tstat
    """

    _fields_ = [
        ('tcpsnd', count_t),
        ('tcpssz', count_t),
        ('tcprcv', count_t),
        ('tcprsz', count_t),
        ('udpsnd', count_t),
        ('udpssz', count_t),
        ('udprcv', count_t),
        ('udprsz', count_t),
        ('avail1', count_t),
        ('avail2', count_t),
        ('cfuture', count_t * 4),
    ]


class TStat(ctypes.Structure):
    """Top level struct to describe multiple statistics categories per task/process.

    C Name: tstat
    C Location: photoproc.h
    """

    _fields_ = [
        ('gen', GEN),
        ('cpu', CPU),
        ('dsk', DSK),
        ('mem', MEM),
        ('net', NET),
    ]