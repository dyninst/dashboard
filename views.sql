--select * from ppc_dev_14c485e_dev_3a2c24f where link='static' and pic='PIC';

--select test,comp,opt,abi,mode,thread,link,pic from arm_dev_14c485e where result IN('FAILED','CRASHED')
--except
--select test,comp,opt,abi,mode,thread,link,pic from arm_master_12c61fc44  where result IN('FAILED','CRASHED');

--select
--    mode.name as mode,
--    link_type.name as link,
--    status.name as status,
--    count(mode) as cnt
--from status,mode,link_type
--left outer join ppc_master_12c61fc44 as res on
--    res.result = status.name
--    and res.mode = mode.name
--    and res.link = link_type.name
--group by mode.name, link_type.name, status.name
--order by mode.name, link_type.name, status.name;
