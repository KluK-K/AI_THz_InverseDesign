import com.comsol.model.*
import com.comsol.model.util.*

% Locked Route B COMSOL template.
%
% Usage from MATLAB with LiveLink:
%   addpath('/Applications/COMSOL64/Multiphysics/mli')
%   mphstart(2037)
%   candidateName = 'B0_straight_cps';
%   run('build_locked_template_from_rectangles.m')
%
% This script intentionally uses the same geometry/material/mesh/study settings
% for every candidate. Do not hand tune settings per structure.

if ~exist('candidateName', 'var') || isempty(candidateName)
    candidateName = 'B0_straight_cps';
end
if ~exist('RUN_SOLVE', 'var') || isempty(RUN_SOLVE)
    RUN_SOLVE = false;
end

projectRoot = fileparts(fileparts(mfilename('fullpath')));
rectPath = fullfile(projectRoot, 'results', 'comsol_rectangles', [candidateName '_rectangles.csv']);
outDir = fullfile(projectRoot, 'results', 'comsol_runs', candidateName);
if ~exist(outDir, 'dir')
    mkdir(outDir);
end

if ~isfile(rectPath)
    error('Rectangle file not found: %s. Run scripts/export_rectangles_for_comsol.py first.', rectPath);
end

rects = readtable(rectPath);

ModelUtil.clear;
model = ModelUtil.create('RouteBLockedTemplate');
model.modelPath(outDir);
model.label([candidateName '.mph']);
model.hist.disable;

geom1 = model.component.create('comp1', true).geom.create('geom1', 3);
geom1.lengthUnit('um');

% Locked parameters
model.param.set('Ltot', '820[um]');
model.param.set('Wbox', '180[um]');
model.param.set('Hsub', '80[um]');
model.param.set('Hair', '120[um]');
model.param.set('Tmet', '0.275[um]');
model.param.set('epsSapphire', '9.3');
model.param.set('tanDeltaSapphire', '1e-4');
model.param.set('sigmaAu', '4.1e7[S/m]');
model.param.set('hmaxBulk', '12[um]');
model.param.set('hmaxMetalNear', '2[um]');
model.param.set('hmin', '0.25[um]');

% Domains
blkSub = geom1.feature.create('blkSub', 'Block');
blkSub.label('Locked sapphire substrate');
blkSub.set('size', {'Ltot', 'Wbox', 'Hsub'});
blkSub.set('pos', {'0', '-Wbox/2', '-Hsub'});
blkSub.set('selresult', true);
blkSub.set('selresultshow', 'all');

blkAir = geom1.feature.create('blkAir', 'Block');
blkAir.label('Locked air box');
blkAir.set('size', {'Ltot', 'Wbox', 'Hair'});
blkAir.set('pos', {'0', '-Wbox/2', '0'});
blkAir.set('selresult', true);
blkAir.set('selresultshow', 'all');

% Metal rectangles
metalTags = {};
for ii = 1:height(rects)
    tag = sprintf('au%04d', ii);
    metalTags{end+1} = tag; %#ok<SAGROW>
    blk = geom1.feature.create(tag, 'Block');
    blk.label(sprintf('Au %s %04d', string(rects.layer(ii)), ii));
    blk.set('size', {sprintf('%.9g', rects.w_um(ii)), sprintf('%.9g', rects.h_um(ii)), 'Tmet'});
    blk.set('pos', {sprintf('%.9g', rects.x_um(ii)), sprintf('%.9g', rects.y_um(ii)), '0'});
    blk.set('selresult', true);
    blk.set('selresultshow', 'all');
end

geom1.run;

% =========================================================
% Coordinate-based port terminal selections
% =========================================================
% Do not use raw boundary IDs. These Box selections target the Au end faces
% by locked coordinates and should remain stable for B0/B1/B2/B3 as long as
% the feed geometry is unchanged.
%
% CPS rail coordinates:
%   upper rail y: +1.5 to +4.5 um
%   lower rail y: -4.5 to -1.5 um
%   Au z:          0 to 0.275 um
%   input x:       0 um
%   output x:      820 um
%
% These selections are terminal candidates for a differential lumped port.
% The actual Lumped Port/Terminal physics must be confirmed on B0 before
% solving and then reused without per-candidate edits.
create_port_box_selection(model, 'sel_p1_plus',  '-0.02',  '0.02',  '1.45',  '4.55',  '-0.02',  '0.295');
create_port_box_selection(model, 'sel_p1_minus', '-0.02',  '0.02', '-4.55', '-1.45',  '-0.02',  '0.295');
create_port_box_selection(model, 'sel_p2_plus',  '819.98', '820.02', '1.45',  '4.55',  '-0.02',  '0.295');
create_port_box_selection(model, 'sel_p2_minus', '819.98', '820.02','-4.55', '-1.45',  '-0.02',  '0.295');

% Materials
matSub = model.component('comp1').material.create('matSub', 'Common');
matSub.label('Locked sapphire');
matSub.propertyGroup('def').set('relpermittivity', {'epsSapphire'});
matSub.propertyGroup('def').set('relpermeability', {'1'});
matSub.propertyGroup('def').set('electricconductivity', {'0'});
matSub.selection.named('geom1_blkSub_dom');

matAir = model.component('comp1').material.create('matAir', 'Common');
matAir.label('Locked air');
matAir.propertyGroup('def').set('relpermittivity', {'1'});
matAir.propertyGroup('def').set('relpermeability', {'1'});
matAir.propertyGroup('def').set('electricconductivity', {'0'});
matAir.selection.named('geom1_blkAir_dom');

matAu = model.component('comp1').material.create('matAu', 'Common');
matAu.label('Locked gold');
matAu.propertyGroup('def').set('electricconductivity', {'sigmaAu'});
matAu.propertyGroup('def').set('relpermittivity', {'1'});
matAu.propertyGroup('def').set('relpermeability', {'1'});
for ii = 1:numel(metalTags)
    try
        matAu.selection.named(['geom1_' metalTags{ii} '_dom']);
    catch
        % COMSOL only permits one named selection here in some versions; final
        % domain selection may need interactive consolidation if this fails.
    end
end

% Mesh. Conservative first locked setting; if changed, rerun all candidates.
mesh1 = model.component('comp1').mesh.create('mesh1');
size1 = mesh1.feature.create('size1', 'Size');
size1.set('custom', true);
size1.set('hmax', 'hmaxBulk');
size1.set('hmin', 'hmin');
size1.set('hcurve', '0.25');
size1.set('hnarrow', '0.8');
ftet1 = mesh1.feature.create('ftet1', 'FreeTet');
ftet1.selection.geom('geom1', 3);
ftet1.selection.all;
mesh1.run;

% Frequency-domain EMW scaffold. Lumped differential port physics is not
% added automatically yet. First confirm sel_p1_plus/minus and sel_p2_plus/minus
% on B0; then encode the port feature here and reuse it for all candidates.
emw = model.component('comp1').physics.create('emw', 'ElectromagneticWaves', 'geom1');

stdMini = model.study.create('stdMini');
stdMini.label('Port locking mini-test frequencies');
stdMini.create('freq', 'Frequency');
stdMini.feature('freq').set('plist', '0.3[THz] 0.8[THz] 1.2[THz]');

stdFull = model.study.create('stdFull');
stdFull.label('Locked full sweep');
stdFull.create('freq', 'Frequency');
stdFull.feature('freq').set('plist', 'range(0.05[THz],0.025[THz],2[THz])');

model.save(fullfile(outDir, [candidateName '_locked_template_geometry.mph']));

summaryPath = fullfile(outDir, [candidateName '_locked_template_status.json']);
fid = fopen(summaryPath, 'w');
fprintf(fid, '{\n');
fprintf(fid, '  "candidate": "%s",\n', candidateName);
fprintf(fid, '  "rectangles_csv": "%s",\n', rectPath);
fprintf(fid, '  "mph": "%s",\n', fullfile(outDir, [candidateName '_locked_template_geometry.mph']));
fprintf(fid, '  "run_solve": %s,\n', lower(string(RUN_SOLVE)));
fprintf(fid, '  "port_strategy": "coordinate_selected_differential_lumped_terminal_pair",\n');
fprintf(fid, '  "port_selections": ["sel_p1_plus", "sel_p1_minus", "sel_p2_plus", "sel_p2_minus"],\n');
fprintf(fid, '  "mini_test_frequencies_thz": [0.3, 0.8, 1.2],\n');
fprintf(fid, '  "status": "geometry_mesh_studies_coordinate_port_selections_created_lumped_port_physics_pending"\n');
fprintf(fid, '}\n');
fclose(fid);

disp(['Saved locked template geometry for ' candidateName]);

function create_port_box_selection(model, tag, xmin, xmax, ymin, ymax, zmin, zmax)
    sel = model.component('comp1').selection.create(tag, 'Box');
    sel.label(tag);
    sel.geom('geom1', 2);
    sel.set('entitydim', 2);
    sel.set('xmin', xmin);
    sel.set('xmax', xmax);
    sel.set('ymin', ymin);
    sel.set('ymax', ymax);
    sel.set('zmin', zmin);
    sel.set('zmax', zmax);
    try
        sel.set('condition', 'intersects');
    catch
        % Some COMSOL versions expose only the default box condition.
    end
end
