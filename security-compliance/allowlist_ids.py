KNOWN_CLINICS = {'KSM-01', 'VIH-01', 'HBA-01'}


def clinic_or_400(clinic_id: str) -> str:
    cid = clinic_id.strip().upper()
    if cid not in KNOWN_CLINICS:
        raise ValueError('unknown clinic_id')
    return cid


if __name__ == '__main__':
    assert clinic_or_400(' ksm-01 ') == 'KSM-01'   # normalise, then decide
    assert clinic_or_400('VIH-01') == 'VIH-01'
    for bad in ('KSM-99', '', 'KSM-01; DROP TABLE'):
        try:
            clinic_or_400(bad)
        except ValueError:
            pass
        else:
            raise AssertionError('allowlist let through: ' + repr(bad))
    print('allowlist_ids OK', len(KNOWN_CLINICS), 'clinics, 3 refusals')