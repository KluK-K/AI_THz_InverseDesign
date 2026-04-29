% B0-first locked template build.
%
% Start COMSOL server separately if needed:
%   /Applications/COMSOL64/Multiphysics/bin/comsol mphserver -port 2037
%
% Then in MATLAB:
%   addpath('/Applications/COMSOL64/Multiphysics/mli')
%   mphstart(2037)
%   run('run_B0_first_locked_template.m')

candidateName = 'B0_straight_cps';
RUN_SOLVE = false;
run('build_locked_template_from_rectangles.m');

